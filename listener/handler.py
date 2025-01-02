import json
import boto3

# Initialize SES client
ses_client = boto3.client("ses", region_name="eu-west-1")  # Replace with your AWS region

def handler(event, context):
    try:
        print("Received event:", json.dumps(event))  # Log the event for debugging

        # Extract recipient email and name from the event
        detail = event.get("detail", {})
        recipient_email = detail.get("email", "recipient@example.com")  # Replace with a verified email for testing
        given_name = detail.get("given_name", "User")

        # Email content
        subject = "Welcome to Task Management!"
        body_text = f"Hi {given_name},\n\nWelcome to our Task Management system! We're excited to have you onboard.\n\n#awsEventBridge"

        # Sending email using SES
        response = ses_client.send_email(
            Source="zaidanali028@gmail.com",  # Replace with your verified sender email
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