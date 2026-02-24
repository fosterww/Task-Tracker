class AppError(Exception):
    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class TaskNotFoundError(AppError):
    def __init__(self):
        super().__init__("Task not found or access denied")


class UserNotFoundError(AppError):
    def __init__(self):
        super().__init__("User not found")


class UserAlreadyExistsError(AppError):
    def __init__(self):
        super().__init__("User with this email already exists")


class AuthenticationError(AppError):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message)


class DatabaseIntegrityError(AppError):
    pass
