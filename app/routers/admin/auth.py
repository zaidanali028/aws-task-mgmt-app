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
    return {"message": "Admin area"}

# Pydantic model for login data


@router.post("/login", summary="Admin Login")
async def admin_login(credentials: AdminUserLogin):
    """
    Authenticate an admin user and return an access token with user details.
    """
    try:
        # Generate the secret hash
        secret_hash = utils.generate_secret_hash(
            my_env_vars.get("COGNITO_APP_CLIENT_ID"),
            my_env_vars.get("COGNITO_APP_CLIENT_SECRET"),
            credentials.email
        )

        # Authenticate the user with Cognito
        response = cognito_client.initiate_auth(
            ClientId=my_env_vars.get("COGNITO_APP_CLIENT_ID"),
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': credentials.email,
                'PASSWORD': credentials.password,
                'SECRET_HASH': secret_hash
            }
        )

        # Retrieve tokens
        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']

        # Decode the access token to get user info
        decoded_access_token = utils.verify_token(access_token, "Admins")

        # Check user groups
        user_groups = decoded_access_token.get('decoded_token', {}).get('cognito:groups', [])
        if 'Admins' not in user_groups:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an Admin")

        # Fetch user attributes from Cognito
        user_details = cognito_client.get_user(AccessToken=access_token)
        attributes = {attr['Name']: attr['Value'] for attr in user_details['UserAttributes']}
        username = attributes.get('sub', 'N/A')
        email = attributes.get('email', 'N/A')
        given_name = attributes.get('given_name', 'N/A')
        family_name = attributes.get('family_name', 'N/A')

        # Return the response
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

    except cognito_client.exceptions.NotAuthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    except cognito_client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
