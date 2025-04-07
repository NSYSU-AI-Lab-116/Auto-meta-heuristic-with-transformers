# Code Design Patterns

## 1. function define rules

- **Function Naming**: use Upper CamelCase for function names.  ex: `GetUserInfo`, `SetUserName`.
- **Function Parameters**: use snake_case for function parameters. ex: `user_id`, `user_name`. You should always define the type instruction for function parameters and returns

    ```python
    def GetUserInfo(user_id: int = 0) -> int:
        """
        some information here
        """
        return user_id
    ```

## 2. Variable define rules

- **Variable Naming**: use snake_case for variable names. ex: `user_id`, `user_name`. You should always define the type instruction for variables.

    ```python
    user_id: int = 0
    user_name: str = "test"
    ```

## 3. Class define rules

- **Class Naming**: use Upper CamelCase for class names. ex: `UserInfo`, `UserName`.
- **Class Init**: every class should have an `__init__` method to initialize the class variables. You should always define the type instruction for class variables.
- **static Class definition**: static class can only be define in library class.
