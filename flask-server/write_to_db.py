#!/usr/bin/env python3
import certifi
import requests
from pymongo import MongoClient
import argparse


class CommunicateWithDatabase:
    """ constructor """

    def __init__(self):
        # create a client to connect to the database
        self.client = MongoClient(
            "mongodb+srv://dhananjai:eD68qSmbQO7A235T@cluster0.3layqrx.mongodb.net/github?retryWrites=true&w=majority",
            tlsCAFile=certifi.where())

        # extract the database we need
        self.db = self.client.github

        # extract the specific collection
        self.collection = self.db.user_repos

        # parse the usernames
        self.usernames = []

        # The base URL for the API that extracts the repositories for a particular user
        self.base_github_api_url = "https://api.github.com/users/"

    """ populate the database with the names of all the repositories"""

    def populate_database(self):

        # loop over all the names in our username array
        for i in range(len(self.usernames)):
            # extract the current username and update the endpoint url
            current_username = self.usernames[i]
            url = self.base_github_api_url + current_username + "/repos"

            try:
                response = requests.get(url)
                # if we get a successful response
                if response.status_code == 200:

                    # extract all the repository names for this user and save the results in a list
                    repositories = [repository['name'] for repository in response.json()]

                    # Here we are checking to see if the data doesn't exist in the database. If it doesn't exist,
                    # then it is a new entry in our collection. Else, we must update the repositories list for the
                    # existing user
                    does_not_exist, actual_username_data = self.is_username_in_database(current_username)
                    if does_not_exist:
                        current_user_data = {'username': current_username, 'all_repo_names': repositories}
                        self.collection.insert_one(current_user_data)
                        print("Inserted new data for username = " + current_username)

                    else:
                        # update the existing username's "all_repo_names" field with the new set of repositories.
                        new_repository_names = {"$set": {'all_repo_names': repositories}}
                        self.collection.update_one({"username": current_username}, new_repository_names)
                        print("Updated repository names for username = " + current_username)
                else:
                    print("Unable to insert data for: " + current_username)
            except Exception as e:
                print("An error occurred when trying to insert data. Please try again.")

    """
        A setter method to set the usernames class variable to a new set of usernames that come in string format.
    """

    def set_usernames(self, all_usernames_string):
        self.usernames = all_usernames_string.split(",")

    """
        A setter method to set the usernames class variable to a new array.
    """

    def set_username_list(self, new_usernames_list):
        self.usernames = new_usernames_list

    """
        A helper method to determine if a username is in the database
    """

    def is_username_in_database(self, username):
        does_not_exist = self.collection.find_one({"username": username}) is None
        return does_not_exist, self.collection.find_one({"username": username}, {'_id': False})


def main(username_string):
    # create an instance of the class
    database_instance = CommunicateWithDatabase()

    # set the usernames
    database_instance.set_usernames(username_string)

    # populate the database with the repository names for all users, old and new
    database_instance.populate_database()


if __name__ == '__main__':
    # Parse the command line arguments
    parser = argparse.ArgumentParser(prog='Write to DB')
    parser.add_argument('usernames', type=str)
    args = parser.parse_args()
    main(args.usernames)
