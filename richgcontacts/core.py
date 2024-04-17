from __future__ import print_function
import os
import colorama
from datetime import datetime
from PIL import Image

from richgcontacts.people_api import PeopleApi
from richgcontacts.social import Social


def main():
    """
    Try connecting the Google People API.
    Get user contacts.
    Try to update theirs profile pictures.
    """

    print('\n')
    print('-' * 15)
    print("Execution...")
    print('-' * 15)
    print('\n')

    # Init colorama
    colorama.init(wrap=True)

    # Init API object
    api = PeopleApi()

    # Get contacts
    connections = api.get_contacts()

    # Filter, for get only users to manage, and format data
    users = filter_contacts(connections)

    # Prepare array of returned data
    updated_users = []

    for user in users:

        print(f'Contact "{user["display_name"]}"')

        images_path = []

        # Loop on each social networks
        for network in user["networks"]:

            # At first, check if this social network is managed
            is_managed = Social.is_managed(network["network_name"])

            # Show network name and username
            print(f'    {network["network_name"]} : {network["user_name"]}', end="")

            # At first, check if this social network is managed
            if not is_managed:
                print('  \u001b[31m(not managed)\u001b[0m')
                continue

            # Else, instantiate social network object
            obj = Social(network["network_name"], network["user_name"])

            # Get profile picture for this user
            process = obj.download_profile_picture()

            # Init colorama again, because some packages reset it
            colorama.init()

            if process["success"] is False:
                if process["error"] == "user_not_found":
                    print(f"    \u001b[33mWarning: user '{network['user_name']}' was not found. Please check this user name.\u001b[0m")
                elif process["error"] == "user_private":
                    print(f"    \u001b[33mWarning: user '{network['user_name']}' is private.\u001b[0m")
                else:
                    print(f"    \u001b[31mError: {process['error']}\u001b[0m")
            else:
                print('   \u001b[32mOK\u001b[0m')
                images_path.append({"network_name": network["network_name"], "image_path": process["image_path"]})

        # Try to update contact profile picture
        if len(images_path):

            # Get the best image to use
            choosen_image_path = choose_best_image(images_path)

            # Try to update contact profile picture
            result = api.update_contact_photo(choosen_image_path["image_path"], user["resource_name"])

            if len(result):
                updated_users.append(
                    {
                        "success": result["success"],
                        "error": result["error"],
                        "api_result": result["api_result"],
                        "choosen_network": choosen_image_path["network_name"],
                     }
                )

    # TODO : better way to show updated users
    print('\n')
    print('-' * 15)
    print("Updated contacts")
    print('-' * 15)

    if not len(updated_users):
        print('No updated contacts.')
    else:
        for user in updated_users:

            # Check if picture has been correctly updated
            if user["success"]:
                print(user["api_result"][0]["displayName"]+f'   \u001b[32mChoosen newtork data: {user["choosen_network"]}\u001b[0m')
            else:
                print(user["api_result"][0]["displayName"] + f'   \u001b[31mError: {user["error"]}\u001b[0m')


def filter_contacts(connections):
    """
    Filter data returned by Google API 'connections' call, for get only wanted contacts
    :param connections: Google People API object returned by connections().list()
    :return: array
    """

    # Prepare an array of users to return
    formatted_users = []

    # Loop on each contact returned by API
    for person in connections:

        # Get username
        name = person.get('names', [])
        if name:
            user_name = name[0].get('displayName')
        else:
            user_name = '(no name)'

        # Get Instant Messages Data
        contact_imClients_data = person.get('imClients', [])

        if contact_imClients_data:

            # Init user vars
            networks = []

            for data in contact_imClients_data:
                networks.append({
                    "network_name": data["protocol"].lower().replace(' ', ''),
                    "user_name": data["username"],
                })

            # Check if we need to push contact in array
            if len(networks):

                # Append user data
                formatted_users.append({
                    "resource_name": person["resourceName"],
                    "etag": person["etag"],
                    "display_name": user_name,
                    "imClients": contact_imClients_data,
                    "photos": person.get('photos', []),
                    "networks": networks,
                })

    # Return all formatted users
    return formatted_users


def choose_best_image(image_objects):
    """
    Define which is the best image to use
    :param image_objects: list - list of dict, contain images to analyze
    :return: string - path to chosen image
    """

    def get_resolution(path):
        """
        Define which is the best image to use
        :param path: string - path to chosen image
        :return: void - width, height
        """

        # Open image with PIL
        with Image.open(path) as img:
            # Get image resolution
            width, height = img.size
        return width, height

    def get_creation_date(path):
        """
        Define which is the best image to use
        :param path: string - path to chosen image
        :return: string - timestamp
        """

        # Uses the file's last modification date as the creation date
        timestamp = os.path.getmtime(path)
        return datetime.fromtimestamp(timestamp)

    def image_score(image_info):
        """
        Define which is the best image to use
        :param image_info: dict - contain 'network_name' and 'image_path'
        :return: dict - chosen image info
        """

        # Extract additional information about the image
        path = image_info["image_path"]

        size = os.path.getsize(path)
        resolution = get_resolution(path)
        creation_date = get_creation_date(path)

        # Score for image size (normalized)
        size_score = 1 - (size / MAX_SIZE)

        # Score for image resolution (normalized)
        resolution_score = (resolution[0] * resolution[1]) / (MAX_RESOLUTION[0] * MAX_RESOLUTION[1])

        # Score for image creation date (normalized)
        creation_date_score = 1 - ((datetime.now() - creation_date).total_seconds() / MAX_AGE_SECONDS)

        # Score for image source
        is_from_instagram_score = (image_info["network_name"] == "instagram")

        # Combine scores using weighted average
        total_score = (
                        (size_weight * size_score + resolution_weight * resolution_score + creation_date_weight * creation_date_score + is_from_instagram_weight * is_from_instagram_score)
                        / (size_weight + resolution_weight + creation_date_weight + is_from_instagram_weight)
                    )

        # print("NEW IMAGE : "+path)
        #
        # print("size : "+str(size))
        # print("size_score : "+str(size_score))
        #
        # print("resolution : "+str(resolution))
        # print("resolution_score : "+str(resolution_score))
        #
        # print("creation_date : "+str(creation_date))
        # print("creation_date_score : "+str(creation_date_score))
        #
        # print("-------------------------------------")

        return total_score

    # Define maximum values for normalization (by getting max value of each dict in image_objects)
    MAX_SIZE = max(os.path.getsize(image_info["image_path"]) for image_info in image_objects)
    MAX_RESOLUTION = max(get_resolution(image_info["image_path"]) for image_info in image_objects)
    MAX_AGE_SECONDS = (datetime.now() - min(get_creation_date(image_info["image_path"]) for image_info in image_objects)).total_seconds()

    # Define weights for each criterion (if a criteria is more important than another)
    is_from_instagram_weight = 1
    size_weight = 1
    resolution_weight = 2
    creation_date_weight = 1

    # Sort the image paths based on their scores
    sorted_paths = sorted(image_objects, key=image_score, reverse=True)

    return sorted_paths[0]  # Return the path with the highest score after sorting
