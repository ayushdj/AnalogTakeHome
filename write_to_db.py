#!/usr/bin/env python3
import certifi
import requests
from pymongo import MongoClient
import argparse


class WriteToDatabase:
    """ constructor """

    def __init__(self, all_usernames_string):
        # create a client to connect to the database
        self.client = MongoClient(
            "mongodb+srv://dhananjai:eD68qSmbQO7A235T@cluster0.3layqrx.mongodb.net/github?retryWrites=true&w=majority",
            tlsCAFile=certifi.where())

        # extract the database we need
        self.db = self.client.github

        # extract the specific collection
        self.collection = self.db.user_repos

        # parse the usernames
        self.usernames = all_usernames_string.split(",")

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
                    if self.collection.find_one({"user_name": current_username}) is None:
                        current_user_data = {'user_name': current_username, 'all_repo_names': repositories}
                        self.collection.insert_one(current_user_data)
                        print("Inserted new data for username = " + current_username)

                    else:
                        # update the existing username's "all_repo_names" field with the new set of repositories.
                        new_repository_names = {"$set": {'all_repo_names': repositories}}
                        self.collection.update_one({"user_name": current_username}, new_repository_names)
                        print("Updated repository names for username = " + current_username)
                else:
                    print("Unable to insert data for: " + current_username)
            except Exception as e:
                print("An error occurred when trying to insert data. Please try again.")


def main(args):
    # create an instance of the class
    database_instance = WriteToDatabase(args)

    # populate the database with the repository names for all users, old and new
    database_instance.populate_database()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Write to DB')
    parser.add_argument('usernames', type=str)
    args = parser.parse_args()
    main(args.usernames)
