import json
import boto3

# Initialize SES client
ses_client = boto3.client("ses", region_name="eu-west-1")

def handler(event, context):
    try:
        print("Received event:", json.dumps(event))  

        # Extract task details from the event
        detail = event.get("detail", {})
        recipient_email = detail.get("email", "recipient@example.com")  # Replace with actual email mapping
        title = detail.get("title", "No Title")
        updated_fields = detail.get("updated_fields", {})

        # Format updated fields
        updates = "\n".join([f"{key}: {value}" for key, value in updated_fields.items()])

        # Email content
        subject = f"Task Updated: {title}"
        body_text = (
            f"Hello,\n\n"
            f"The task '{title}' has been updated with the following changes:\n\n"
            f"{updates}\n\n"
            f"Please log in to the system to view more details.\n\n"
            f"#awsEventBridge"
        )

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
        return {"statusCode": 200, "body": "Task update email sent successfully!"}

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
