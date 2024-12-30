from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

MY_AWS_REGION = str(os.getenv("MY_AWS_REGION"))
COGNITO_USER_POOL_ID = str(os.getenv("COGNITO_USER_POOL_ID"))
COGNITO_APP_CLIENT_ID = str(os.getenv("COGNITO_APP_CLIENT_ID"))
COGNITO_APP_CLIENT_SECRET = str(os.getenv("COGNITO_APP_CLIENT_SECRET"))
DYNAMODB_TABLE_NAME=str(os.getenv("DYNAMODB_TABLE_NAME"))
COGNITO_JWKS_URL=str(os.getenv("COGNITO_JWKS_URL"))
EVENT_BUS_NAME=str(os.getenv("EVENT_BUS_NAME"))

# Cognito endpoints