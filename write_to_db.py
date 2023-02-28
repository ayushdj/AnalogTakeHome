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
        self.usernames = self._parse_usernames(all_usernames_string)
        print(self.usernames)

    """ we want to split the input as it is a comma separated input """
    def _parse_usernames(self, usernames):
        split_usernames = usernames.split(",")
        actual_usernames = []
        for username in split_usernames:
            result = self.collection.find_one({"user_name": username})
            if result == None:
                actual_usernames.append(username)
        return actual_usernames

    """ populate the database with the names of all the repositories"""
    def populate_database(self):
        # loop over all the names in our global array

        for i in range(len(self.usernames)):
            current_username = self.usernames[i]
            url = "https://api.github.com/users/" + current_username + "/repos"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    repos = [repo['name'] for repo in response.json()]
                    current_user_data = {'user_name': current_username, 'all_repo_names': repos}
                    self.collection.insert_one(current_user_data)
                    print("Inserted data for username = " + current_username)
                else:
                    print("Unable to insert data for: " + current_username)
                    return
            except Exception as e:
                print("an error occurred when trying to insert data. Please try again.")






def main(args):
    database_instance = WriteToDatabase(args)
    database_instance.populate_database()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Write to DB')
    parser.add_argument('usernames', type=str)
    args = parser.parse_args()
    main(args.usernames)
