import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from typing import Optional, List

# Load environment variables
from app.utils import utils

my_env_vars = utils.load_env()

# Initialize Cognito client
cognito_client = boto3.client('cognito-idp', region_name=my_env_vars.get("MY_AWS_REGION"))


# Fetch All Users in a Group
def get_all_users(group_name: str) -> Optional[List[dict]]:
    try:
        user_pool_id = my_env_vars.get("COGNITO_USER_POOL_ID")
        users = []
        pagination_token = None

        while True:
            if pagination_token:
                response = cognito_client.list_users_in_group(
                    UserPoolId=user_pool_id,
                    GroupName=group_name,
                    NextToken=pagination_token
                )
            else:
                response = cognito_client.list_users_in_group(
                    UserPoolId=user_pool_id,
                    GroupName=group_name
                )
            
            for user in response.get('Users', []):
                user_data = {
                    "username": user.get("Username"),
                    "attributes": {attr["Name"]: attr["Value"] for attr in user.get("Attributes", [])}
                }
                users.append(user_data)

            pagination_token = response.get('NextToken')
            if not pagination_token:
                break

        if not users:
            raise HTTPException(status_code=404, detail="No users found")
        return users

    except ClientError as e:
        print(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Error fetching users")


# Create a New User
def create_user(username: str, attributes: dict) -> Optional[dict]:
    try:
        user_pool_id = my_env_vars.get("COGNITO_USER_POOL_ID")
        formatted_attributes = [{"Name": key, "Value": value} for key, value in attributes.items()]

        response = cognito_client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=formatted_attributes
        )
        return response
    except ClientError as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Error creating user")


# Fetch a User by Username
def get_user(username: str) -> Optional[dict]:
    try:
        user_pool_id = my_env_vars.get("COGNITO_USER_POOL_ID")
        response = cognito_client.admin_get_user(
            UserPoolId=user_pool_id,
            Username=username
        )
        return {
            "username": username,
            "attributes": {attr["Name"]: attr["Value"] for attr in response.get("UserAttributes", [])}
        }
    except cognito_client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=404, detail="User not found")
    except ClientError as e:
        print(f"Error fetching user: {e}")
        raise HTTPException(status_code=500, detail="Error fetching user")


# Update User Attributes
def update_user(username: str, attributes: dict) -> Optional[dict]:
    try:
        user_pool_id = my_env_vars.get("COGNITO_USER_POOL_ID")
        formatted_attributes = [{"Name": key, "Value": value} for key, value in attributes.items()]

        cognito_client.admin_update_user_attributes(
            UserPoolId=user_pool_id,
            Username=username,
            UserAttributes=formatted_attributes
        )
        # Fetch updated user details
        return get_user(username)
    except ClientError as e:
        print(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail="Error updating user")


# Delete a User
def delete_user(username: str) -> Optional[dict]:
    try:
        user_pool_id = my_env_vars.get("COGNITO_USER_POOL_ID")
        cognito_client.admin_delete_user(
            UserPoolId=user_pool_id,
            Username=username
        )
        return {"username": username, "message": "User deleted successfully"}
    except cognito_client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=404, detail="User not found")
    except ClientError as e:
        print(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Error deleting user")


