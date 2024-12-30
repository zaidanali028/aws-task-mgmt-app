from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

MY_AWS_REGION = os.getenv("MY_AWS_REGION")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_APP_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")
COGNITO_APP_CLIENT_SECRET = os.getenv("COGNITO_APP_CLIENT_SECRET")
DYNAMODB_TABLE_NAME=os.getenv("DYNAMODB_TABLE_NAME")
COGNITO_JWKS_URL=os.getenv("COGNITO_JWKS_URL")
EVENT_BUS_NAME=os.getenv("EVENT_BUS_NAME")
COGNITO_APP_CLIENT_SECRET2=os.getenv("COGNITO_APP_CLIENT_SECRET2")

# Cognito endpoints