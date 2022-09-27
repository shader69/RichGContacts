from __future__ import print_function

import base64
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from project.globals import *


class PeopleApi:
    """
    Class used to call Google People API

    Attributes
    ----------
    creds : object from google.oauth2.credentials
        token to connect to the api
    SCOPES : string
        authorization type, to ask the user
        if this value is modified, delete the file token.json
        show https://developers.google.com/identity/protocols/oauth2/scopes for more details
    token_path : string
        path to token file
        unique for a connected user
    credentials_path : string
        path to credentials file
        used for access Google People API
        read the README for more details
    service : googleapiclient object
        use to call the API

    Methods
    -------
    connect_api()
        Try to connect user to the api.
    get_contacts()
        Get contacts for a connected user.
    update_contact_photo(image_path, resource_name)
        Update contact profile picture.
    """

    def __init__(self):
        """
        Try connecting the Google People API.
        :return: dict - contains 'api' and 'connections'
        """

        # Init var
        self.creds = None
        self.SCOPES = ['https://www.googleapis.com/auth/contacts']

        # Set paths
        self.token_path = os.path.join(root, f'data/token.json')
        self.credentials_path = os.path.join(root, f'data/credentials.json')

        # Check credentials, and connect user to API
        self.service = None
        self.connect_api()

    def connect_api(self):
        """
        Try to connect user to the api, using "credentials.json".
        Is connection is done, a token file is created, for connected user.
        :return: void
        """

        # Check if credentials file exist
        if not os.path.exists(self.credentials_path):
            exit("Error: missing Google People API 'credentials.json' file. Read the README to get this file, and set it in 'RichGContacts/project/data/'.")

        # The file token.json stores the user's access and refresh tokens, and is created automatically when the
        # authorization flow completes for the first time.
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())

        # Prepare API
        self.service = build('people', 'v1', credentials=self.creds)

    def get_contacts(self):
        """
        Get contacts for a connected user.
        :return: array
        """

        try:

            # Do the call
            results = self.service.people().connections().list(
                resourceName='people/me',
                # pageSize=10,
                sortOrder='LAST_MODIFIED_DESCENDING',
                personFields='names,photos,imClients'
            ).execute()

            # Return contacts
            return results.get('connections', [])

        except HttpError as err:
            exit(f'API HTTP error: {err}')

    def update_contact_photo(self, image_path, resource_name):
        """
        Update contact profile picture.
        :param image_path: string, image to update
        :param resource_name: string, returned by People API connections() call. Unique for each contact.
        :return: array
        """

        # Convert picture to use, into bytes format
        with open(image_path, "rb") as image:
            photo_bytes = base64.b64encode(image.read())

        # Update actual picture with this new picture
        results = self.service.people().updateContactPhoto(
            resourceName=resource_name,
            body={
                "photoBytes": photo_bytes.decode('utf-8'),
                "personFields": "names,photos,imClients"
            }
        ).execute()

        # Return updated results
        return results.get('person', []).get('names', [])
