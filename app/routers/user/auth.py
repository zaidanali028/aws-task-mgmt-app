import boto3
import os
from fastapi import APIRouter, HTTPException,status

import app.utils.utils as utils
from app.models import AdminUserLogin
# Load environment variables from .env file

my_env_vars=utils.load_env()


# Initialize Cognito client
cognito_client = boto3.client('cognito-idp', region_name=my_env_vars.get("MY_AWS_REGION"))

router = APIRouter()


@router.get("/")
async def get_admin_info():
    return {"message": "User area"}


@router.post("/login", summary="User Login")
async def user_login(credentials: AdminUserLogin):
    """
    Authenticate a TeamMember user and return access and refresh tokens with user details.
    """
    try:
        # Generate the secret hash for Cognito authentication
        secret_hash = utils.generate_secret_hash(
            my_env_vars.get("COGNITO_APP_CLIENT_ID"),
            my_env_vars.get("COGNITO_APP_CLIENT_SECRET"),
            credentials.email
        )

        # Authenticate the user with Cognito
        response = cognito_client.initiate_auth(
            ClientId=my_env_vars.get("COGNITO_APP_CLIENT_ID"),
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": credentials.email,
                "PASSWORD": credentials.password,
                "SECRET_HASH": secret_hash
            }
        )

        # Retrieve tokens
        access_token = response["AuthenticationResult"]["AccessToken"]
        refresh_token = response["AuthenticationResult"]["RefreshToken"]

        # Get user details using the access token
        user_details = cognito_client.get_user(AccessToken=access_token)
        user_attributes = {attr["Name"]: attr["Value"] for attr in user_details.get("UserAttributes", [])}

        # Extract specific user attributes
        username = user_details.get("Username")
        email = user_attributes.get("email")
        given_name = user_attributes.get("given_name", "N/A")
        family_name = user_attributes.get("family_name", "N/A")

        # Decode the access token to extract group membership
        decoded_access_token = utils.verify_token(access_token, "TeamMembers")
        user_groups = decoded_access_token.get("decoded_token", {}).get("cognito:groups", [])

        # Ensure the user is in the "TeamMembers" group
        if "TeamMembers" not in user_groups:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a TeamMember"
            )

        # Return the detailed response
        return {
            "access_token": access_token,
            "user": {
                "username": username,
                "email": email,
                "given_name": given_name,
                "family_name": family_name,
                "user_group": user_groups
            }
        }

    except cognito_client.exceptions.NotAuthorizedException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    except cognito_client.exceptions.UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )