class AppInterfaceException(Exception):
    pass

class UserNotFoundError(AppInterfaceException):
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.message = f"User with id {user_id} does not exist"

class ItemNotFounError(AppInterfaceException):
    def __init__(self, item_id: int):
        self.item_id = item_id
        self.message = f"Todo with id {item_id} not found"
