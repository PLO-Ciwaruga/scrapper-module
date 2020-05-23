"""
    PLO-Ciwaruga

    Simple Auth Class
    22/05/2020
"""

import json
import bcrypt
from typing import List
from Auth import User


class Auth:
    path: str
    rawDict: dict
    users: List[User]

    def __init__(self, authFilePath: str = 'auth.json'):
        self.path = authFilePath
        self.users = []

        self.__load(authFilePath)

        if self.isEmpty():
            print('[INFO] Auth is empty! Any auth will be authorized!')

    def __load(self, path: str):
        print('[INFO] Loading up users list from %s' % (path))
        try:
            with open(path, 'r') as source_file:
                rawDict = json.load(source_file)

            self.rawDict = rawDict
            usersList = rawDict['users']
            for user in usersList:
                tempUser = User(user['username'], user['role'],
                                user['pass_hash'])

                self.users.append(tempUser)

        except json.JSONDecodeError as JDE:
            print('[ERROR] Auth file error ', JDE)
            print('[INFO] Creating new empty auth file')

            empty_auth = {
                'users': []
            }

            with open(path, 'w') as dest_file:
                json.dump(empty_auth, dest_file)

            self.__load(path)

    def auth(self, username, raw_pass) -> bool:
        if self.isEmpty():
            return True

        pass_hash, usr_role = self.__search(username)

        if pass_hash == None:
            return False

        if bcrypt.checkpw(raw_pass.encode(), pass_hash):
            return True

        return False

    def __search(self, username) -> (str, str):
        for user in self.users:
            if user.username == username:
                return user.pass_hash.encode(), user.role
        else:
            return None, None

    def getRole(self, username):
        if self.isEmpty():
            return 'admin'
        pass_hash, usr_role = self.__search(username)

        return usr_role

    def __saltAndHash(self, raw_pass) -> str:
        salt = bcrypt.gensalt()
        raw_pass = raw_pass.encode()

        return bcrypt.hashpw(raw_pass, salt).decode()

    def __add(self, user):
        tempUser = {
            'username': user.username,
            'pass_hash': user.pass_hash,
            'role': user.role
        }
        self.rawDict['users'].append(tempUser)
        self.users.append(user)

        with open(self.path, 'w') as dest_file:
            json.dump(self.rawDict, dest_file)

    def newUser(self, username, password, role):
        pass_hash, usr_role = self.__search(username)

        if pass_hash == None and usr_role == None:
            tempUsr = User(username, role, self.__saltAndHash(password))

            self.__add(tempUsr)

            return True
        else:
            return False

    def isEmpty(self):
        if len(self.users) == 0:
            return True
        else:
            return False
