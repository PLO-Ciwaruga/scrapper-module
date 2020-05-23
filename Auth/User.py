"""
    PLO-Ciwaruga

    Simple Auth Class, User Data Type
    23/05/2020
"""


class User:
    username: str
    role: str
    pass_hash: str

    def __init__(self, username: str, role: str, pass_hash: str) -> None:
        self.username = username
        self.role = role
        self.pass_hash = pass_hash
