import glob
import sys
from os.path import exists
from datetime import datetime

# Instagram
import instaloader
from instaloader import Profile, ProfileNotExistsException

# Facebook
from facebook_scraper import get_profile

import requests
from requests import HTTPError
import warnings

from PIL import Image

from richgcontacts.globals import *


class Social:
    """
    Create an object associated to a social network.
    Use it to return profile picture for a user.

    Attributes
    ----------
    network_name : string
        Name of the network
    user_name : string
        Name of the user, for this network

    Methods
    -------
    is_managed(network_name)
        Check if wanted social network is managed.
    download_profile_picture()
        Redirect to another function, using the network name.
    download_profile_picture__instagram()
        Use Instaloader, to get an Instagram profile picture.
    download_profile_picture__facebook()
        Use facebook-scraper, to get a Facebook profile picture.
    get_profile_pictures(get_only_last)
        Return downloaded image, for a specific user and social network, order by modified date DESC.
    delete_duplicated_image()
        Check if the last downloaded image is identical to the previous one, and delete it if it's true.
    """

    # Managed social networks
    NETWORKS = ["instagram", "facebook"]

    # Instantiate external packages (only one time)
    IG = None

    def __init__(self, network_name, user_name):
        """
        Init the social network object.
        :param network_name: string - must be in NETWORKS array.
        :param user_name: string - for this network type.
        """

        # Check if wanted social network is managed
        if not self.is_managed(network_name):
            exit(f"Error: the social network '{network_name}' is not managed.")

        # If no errors, init object
        self.network_name = network_name
        self.user_name = user_name

        # Instantiate other packages if necessary
        self.instantiate_external_package()

    @classmethod
    def is_managed(cls, network_name):
        """
        Check if wanted social network is managed.
        :param network_name: string
        :return: bool
        """

        return network_name in cls.NETWORKS

    def instantiate_external_package(self):
        """
        Only redirect to the correct function, using the network name.
        :return: void|dict - void if object has already been instantiated, or dict if there is an error during the process
        """

        if self.network_name not in self.NETWORKS:
            exit("Not managed network.")

        # Redirect, using self.network_name
        return eval('self.instantiate_external_package__'+self.network_name+'()')

    def instantiate_external_package__instagram(self):
        """
        Instantiate "instaloader" package
        :return: void|dict - void if object has already been instantiated, or dict if there is an error during the process
        """

        # Do not process if object has already been instantiated
        if Social.IG is not None:
            return

        try:
            # Prepare file path
            folder_path = os.path.join(userdata_path, self.network_name)
            folder_path = os.path.join(folder_path, '{target}')

            # Init Instaloader
            Social.IG = instaloader.Instaloader(dirname_pattern=folder_path, quiet=True)

            # Overwrite function, for disable print errors
            def nothing(msg, repeat_at_end=True):
                pass
            Social.IG.context.error = nothing
            
        except Exception as err:
            return {
                "success": False,
                "error": str(err),
            }

    def instantiate_external_package__facebook(self):
        """
        Instantiate "facebook-scrapper" package
        :return: void - nothing to return
        """

        # Nothing to instantiate
        return

    def download_profile_picture(self):
        """
        Only redirect to the correct function, using the network name.
        :return: dict - success of the process
        """

        if self.network_name not in self.NETWORKS:
            exit("Not managed network.")

        # Redirect, using self.network_name
        return eval('self.download_profile_picture__'+self.network_name+'()')

    def download_profile_picture__instagram(self):
        """
        Use Instaloader, to get an Instagram profile picture.
        :return: dict - success of the process, and image path
        """

        try:

            # Instantiate instaloader.Profile class, for given user_name
            user_profile = Profile.from_username(Social.IG.context, self.user_name)

            # Download image to 'user data' folder
            # Social.IG.download_profile(user_name, profile_pic_only=True)
            Social.IG.download_profilepic(user_profile)

            # If no errors, get downloaded image path
            image_path = self.get_profile_pictures()

            # Return latest image
            return {
                "success": True,
                "error": None,
                "image_path": image_path,
            }

        except ProfileNotExistsException:
            return {
                "success": False,
                "error": "user_not_found",
            }
        except Exception as err:
            return {
                "success": False,
                "error": str(err),
            }

    def download_profile_picture__facebook(self):
        """
        Use facebook-scraper, to get a Facebook profile picture.
        :return: dict - success of the process, and image path
        """

        try:

            # Disable module warnings
            old_warnings_filters = warnings.filters
            warnings.filterwarnings('ignore')

            # Disable print return
            # sys.stdout = open(os.devnull, 'w')
            # sys.stderr = open(os.devnull, 'w')

            # Use facebook-scraper, for trying to get user data
            profile_data = get_profile(self.user_name)

            # Re-activate module warnings
            warnings.filters = old_warnings_filters

            # Enable print return
            # sys.stdout = sys.__stdout__
            # sys.stderr = sys.__stderr__

            # Check if user has been found
            if profile_data["Name"] == "Contenu introuvable":
                return {
                    "success": False,
                    "error": "user_not_found",
                }

            # If no except, try to get profile picture
            if not profile_data["profile_picture"]:
                return {
                    "success": False,
                    "error": "picture_not_found",
                }

            # Get image URL
            profile_picture_url = profile_data["profile_picture"]

            # Download photo_url, and store it
            image_path = self.save_profile_picture(profile_picture_url)

            # Return latest image
            return {
                "success": True,
                "error": None,
                "image_path": image_path,
            }

        except HTTPError as err:
            if '404' in str(err):
                return {
                    "success": False,
                    "error": "user_not_found",
                }
            else:
                return {
                    "success": False,
                    "error": "http_error",
                }
        except Exception as err:
            if '(cookies) is required' in str(err):
                return {
                    "success": False,
                    "error": "user_private",
                }
            else:
                return {
                    "success": False,
                    "error": str(err),
                }

    def save_profile_picture(self, photo_url):
        """
        Download given image URL, and save it in the correct path.
        :param photo_url: string - image URl to query
        :return: string - image path
        """

        # Prepare file name to set
        if len(self.get_profile_pictures(False)):
            date_to_use = datetime.now()
        else:
            date_to_use = datetime(1971, 1, 1)

        file_name = date_to_use.strftime("%Y-%m-%d_%H-%M-%S") + '.jpg'

        file_date = date_to_use.timestamp()

        # Prepare file path
        folder_path = os.path.join(userdata_path, self.network_name)
        folder_path = os.path.join(folder_path, self.user_name)
        file_path = os.path.join(folder_path, file_name)

        # Create folder if not exist
        if not os.path.exists(folder_path):
            os.makedirs(os.path.join(folder_path))

        # Create an empty file
        if not exists(file_path):

            # Télécharger la photo de profil
            response = requests.get(photo_url)

            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
            else:
                raise Exception("Impossible de télécharger la photo de profil.")

            # with open(file_path, 'wb') as handle:
            #
            #     # Get image content
            #     response = requests.get(photo_url, stream=True)
            #
            #     if not response.ok:
            #         print(response)
            #
            #     # Fill the empty file with image content
            #     for block in response.iter_content(1024):
            #         if not block:
            #             break
            #
            #         handle.write(block)

            # Set file dates (first parameter is atime, and second is mtime)
            os.utime(file_path, (file_date, file_date))

        # Delete this image if it's the same as the previous
        self.delete_duplicated_image()

        # If no errors, get last image path
        image_path = self.get_profile_pictures()

        return image_path

    def get_profile_pictures(self, get_only_last=True):
        """
        Return downloaded image, for a specific user and social network, order by modified date DESC.
        :param get_only_last: bool - return only last images, or all images
        :return: array|string - contains image path
        """

        # Get image path
        image_path = os.path.join(userdata_path, self.network_name)
        image_path = os.path.join(image_path, self.user_name)

        # Filter only images
        files = glob.glob(image_path + '/*.jpg')

        # Order files by modified date ASC
        paths = sorted(files, key=os.path.getmtime)

        # Reverse array
        paths.reverse()

        # Return latest image
        if len(paths) and get_only_last is True:
            return paths[0]
        elif len(paths) and get_only_last is False:
            return paths
        elif not len(paths) and get_only_last is False:
            return []
        else:
            return None

    def delete_duplicated_image(self):
        """
        Check if the last downloaded image is identical to the previous one, and delete it if it's true.
        :return: void
        """

        # Get image path
        images = self.get_profile_pictures(False)

        if len(images) < 2:
            return

        im1 = Image.open(images[0])
        im2 = Image.open(images[1])

        # If images are identical, we delete the last one
        if list(im1.getdata()) == list(im2.getdata()):
            os.remove(images[0])
