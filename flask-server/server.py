import certifi
from flask import Flask, jsonify, request
from pymongo import MongoClient
from write_to_db import CommunicateWithDatabase

app = Flask(__name__)

# use the CommunicateWithDatabase class to create a connection to the database
database_connection = CommunicateWithDatabase()

"""
    gets the repository names for one user
"""


@app.route('/user/<username>', methods=['GET'])
def get_data_by_username(username):
    does_not_exist, actual_username_data = database_connection.is_username_in_database(username)
    return jsonify({'result': actual_username_data})


"""
    get all the repository names for a group of users
"""


@app.route('/users', methods=['GET'])
def get_data_for_all_users():
    data = request.get_json()

    # set the "usernames" class variable
    database_connection.set_username_list(eval(data["usernames"]))

    # initialize our result list
    result = []

    # loop over all the usernames
    for username in database_connection.usernames:
        # extract the actual data and only if the user exists in the database do we append the data.
        does_not_exist, actual_username_data = database_connection.is_username_in_database(username)
        result.append({username: actual_username_data})

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
