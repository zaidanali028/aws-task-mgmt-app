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

# Pydantic model for login data


@router.post("/login")
async def user_login(credentials: AdminUserLogin):
  
    try:
        # print(COGNITO_APP_CLIENT_ID, COGNITO_APP_CLIENT_SECRET)
        secret_hash=utils.generate_secret_hash(my_env_vars.get("COGNITO_APP_CLIENT_ID"), my_env_vars.get("COGNITO_APP_CLIENT_SECRET"), credentials.email)
        secret_hash_2=utils.generate_secret_hash(my_env_vars.get("COGNITO_APP_CLIENT_ID"), '11s42a3hm384b96efdgdmiq7e7v6inh819nk691e89k0ilsa4bac', credentials.email)
        # Try to authenticate the user with the provided email and password
        response = cognito_client.initiate_auth(
            ClientId=my_env_vars.get("COGNITO_APP_CLIENT_ID"),
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': credentials.email,
                'PASSWORD': credentials.password,
                'SECRET_HASH': secret_hash_2  # Include the SECRET_HASH here
            }
            
        )
        
        # return response

        # Retrieve the tokens from the authentication result
        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']

        # Verify that the user is in the 'Admin' group
        

         # Decode the access token to get user information (username or 'sub')
        decoded_access_token = utils.verify_token(access_token, "TeamMembers")
         # Check if 'Admin' group exists in the decoded token
        user_groups = decoded_access_token.get('decoded_token').get('cognito:groups', [])
        
        print(user_groups)
       
        
        
        if 'TeamMembers' not in user_groups:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a TeamMember")

        else:
            print("User is a TeamMember")
        # Return the tokens if the user is an Admin
        return {
            # "id_token": id_token,
            "access_token": access_token,
            # "refresh_token": refresh_token
        }
       


    except cognito_client.exceptions.NotAuthorizedException as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
   
        
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
