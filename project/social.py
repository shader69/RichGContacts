import glob
import sys

import instaloader
from instaloader import Profile, ProfileNotExistsException

from project.globals import *


class Social:
    """
    Create an object associated to a social network.
    Use it to return profile picture for a user.
    """

    # Managed social networks
    NETWORKS = ["instagram", "facebook"]

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

    @classmethod
    def is_managed(cls, network_name):
        """
        Check if wanted social network is managed.
        :param network_name: string
        :return: bool
        """

        return network_name in cls.NETWORKS

    def get_profile_picture(self):
        """
        Only redirect to the correct function, using the network name.
        :return:
        """

        # Redirect, using self.name
        if self.network_name == "instagram":
            return self.get_profile_picture__instagram()
        elif self.network_name == "facebook":
            return self.get_profile_picture__facebook()
        else:
            exit("Not managed network.")

    def get_profile_picture__instagram(self):
        """
        Use Instaloader to get profile picture
        :return: string - image path
        """

        try:

            # Init Instaloader
            self.ig = instaloader.Instaloader(dirname_pattern=userdata_path + '{target}/instagram')

            # Instantiate instaloader.Profile class
            user_profile = Profile.from_username(self.ig.context, self.user_name)

            # Disable print return
            sys.stdout = open(os.devnull, 'w')

            # Download image to 'user data' folder
            # self.ig.download_profile(user_name, profile_pic_only=True)
            self.ig.download_profilepic(user_profile)

            # Enable print return
            sys.stdout = sys.__stdout__

            # If no errors, get image path
            image_path = os.path.join(userdata_path, self.user_name+'/instagram/')

            # Filter only images
            files = glob.glob(image_path + '/*.jpg')

            # Order files by modified date ASC
            paths = sorted(files, key=os.path.getmtime)

            # Reverse array
            paths.reverse()

            # Return latest image
            return {
                "success": True,
                "error": None,
                "image_path": paths[0],
            }

        except ProfileNotExistsException:
            return {
                "success": False,
                "error": "user_not_found",
            }
        except:
            return {
                "success": False,
                "error": "unmatched",
            }

    def get_profile_picture__facebook(self):
        return {
            "success": False,
            "error": "unmatched",
        }