import json
import boto3

# Initialize SES client
ses_client = boto3.client("ses", region_name="eu-west-1")  

def handler(event, context):
    try:
        print("Received event:", json.dumps(event))  

        # Extracting recipient email, password, and name from the event
        detail = event.get("detail", {})
        recipient_email = detail.get("email", "recipient@example.com")  
        given_name = detail.get("given_name", "User")
        user_password = detail.get("user_password", "")

        # Email content
        subject = "Welcome to Task Management!"
        body_text = f"Hi {given_name},\n\nWelcome to our Task Management system! We're excited to have you onboard.\nYou can find your login credentials below:\n\nEmail: {recipient_email}\nPassword: {user_password}\n\n#awsEventBridge"

        # Sending email using SES
        response = ses_client.send_email(
            Source="zaidanali028@gmail.com",  # Verified email on SES
            Destination={"ToAddresses": [recipient_email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body_text}},
            },
        )
        print(f"Email sent successfully: {response}")
        return {"statusCode": 200, "body": "Email sent successfully!"}

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
