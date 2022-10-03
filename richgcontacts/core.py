from __future__ import print_function

import colorama

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

            # Show network name and user name
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
                    print(f"   \u001b[33mWarning: user '{network['user_name']}' was not found. Please check this user name.\u001b[0m")
                elif process["error"] == "user_private":
                    print(f"   \u001b[33mWarning: user '{network['user_name']}' is private.\u001b[0m")
                else:
                    print(f"   \u001b[31mError: {process['error']}\u001b[0m")
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
                updated_users.append({"api_result": result, "choosen_network": choosen_image_path["network_name"]})

    # TODO : better way to show updated users
    print('\n')
    print('-' * 15)
    print("Updated contacts")
    print('-' * 15)

    for user in updated_users:
        print(user["api_result"][0]["displayName"]+f'   \u001b[32mChoosen newtork data: {user["choosen_network"]}\u001b[0m')


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
                    "network_name": data["protocol"].lower(),
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


def choose_best_image(images_path):
    """
    Define which is the best image to use
    :param images_path: array - array of object, contain images to analyze
    :return: string - path to chosen image
    """

    # If there is only one image, return it
    if len(images_path) == 1:
        return images_path[0]

    # Else compare the images
    # TODO : do a real method to determine which is best image to use
    return images_path[0]
