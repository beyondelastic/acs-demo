import json
import datetime
from typing import Any, Callable, Set, Dict, List, Optional
import os
from dotenv import load_dotenv
from azure.communication.email import EmailClient
import base64

# Load environment variables from .env file
load_dotenv()


def fetch_current_datetime(format: Optional[str] = None) -> str:
    """
    Get the current time as a JSON string, optionally formatted.

    :param format (Optional[str]): The format in which to return the current time. Defaults to None, which uses a standard format.
    :return: The current time in JSON format.
    :rtype: str
    """
    current_time = datetime.datetime.now()

    # Use the provided format if available, else use a default format
    if format:
        time_format = format
    else:
        time_format = "%Y-%m-%d %H:%M:%S"

    time_json = json.dumps({"current_time": current_time.strftime(time_format)})
    return time_json


def send_email(recipient: str, subject: str, body: str, acs_connection_string: Optional[str] = None, sender: Optional[str] = None, file_path: Optional[str] = None) -> str:
    """
    Sends an email using Azure Communication Services Email, with optional file attachment.
    """
    try:
        if acs_connection_string is None:
            acs_connection_string = os.getenv("AZURE_COMMUNICATION_SERVICE_CONNECTION_STRING")
        if sender is None:
            sender = os.getenv("AZURE_COMMUNICATION_SERVICE_SENDER")
        if not acs_connection_string or not sender:
            return json.dumps({"error": "Missing ACS connection string or sender email."})

        email_client = EmailClient.from_connection_string(acs_connection_string)
        message = {
            "content": {
                "subject": subject,
                "plainText": body,
                "html": f"<html><body>{body}</body></html>"
            },
            "recipients": {
                "to": [
                    {
                        "address": recipient,
                        "displayName": recipient.split('@')[0]
                    }
                ]
            },
            "senderAddress": sender
        }
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    file_bytes = f.read()
                file_name = os.path.basename(file_path)
                import mimetypes
                mime_type, _ = mimetypes.guess_type(file_name)
                if not mime_type:
                    mime_type = "application/octet-stream"
                attachment = {
                    "name": file_name,
                    "contentType": mime_type,
                    "contentInBase64": base64.b64encode(file_bytes).decode()
                }
                message["attachments"] = [attachment]
            except Exception as e:
                return json.dumps({"error": f"Failed to attach file: {str(e)}"})
        poller = email_client.begin_send(message)
        result = poller.result()
        # Print the full result for diagnostics
        print(f"[DEBUG] Email send result object: {result}")
        # Improved success check: if no exception, treat as success
        if hasattr(result, "status") and getattr(result, "status", None) == "Succeeded":
            return json.dumps({"message": f"Email successfully sent to {recipient}."})
        elif not hasattr(result, "status") or getattr(result, "status", None) is None:
            return json.dumps({"message": f"Email sent to {recipient} (status unknown, but no error was raised)."})
        else:
            return json.dumps({"error": f"Failed to send email: {getattr(result, 'error', 'Unknown error')}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


user_functions: Set[Callable[..., Any]] = {
    send_email, 
    fetch_current_datetime,
}

