from __future__ import print_function

import colorama

from project.people_api import PeopleApi

from project.social import Social


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

        # Define which is the best image to use # TODO : better way to determine which is best image to use
        image_path = None

        # Loop on each social networks
        for network in user["networks"]:

            # At first, check if this social network is managed
            is_managed = Social.is_managed(network["network_name"])

            string = f'    {network["network_name"]} : {network["user_name"]}'
            if not is_managed:
                string = string + ' \u001b[31m(not managed)\u001b[0m'

            print(string)

            # At first, check if this social network is managed
            if not is_managed:
                continue

            # Else, instantiate social network object
            obj = Social(network["network_name"], network["user_name"])

            # Get profile picture for this user
            process = obj.download_profile_picture()

            # Init colorama again, because some packages reset it
            colorama.init()

            if process["success"] is False:
                if process["error"] == "user_not_found":
                    print(f"\u001b[33mWarning: contact '{user['display_name']}' was not found. Please check this user name.\u001b[0m")
                else:
                    print("\u001b[31mError: an error occurred. Please retry later.\u001b[0m")
            else:
                image_path = process["image_path"]

        # Try to update contact profile picture
        if image_path is not None:
            result = api.update_contact_photo(image_path, user["resource_name"])

            if len(result):
                updated_users.append(result)

    # TODO : better way to show updated users
    print('\n')
    print('-' * 15)
    print("Updated contacts")
    print('-' * 15)

    for user in updated_users:
        print(user[0]["displayName"])


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
