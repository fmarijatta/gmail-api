import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]



creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists("token.json"):
  creds = Credentials.from_authorized_user_file("token.json", SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
  if creds and creds.expired and creds.refresh_token:
    creds.refresh(Request())
  else:
    flow = InstalledAppFlow.from_client_secrets_file(
        "credentials.json", SCOPES
    )
    creds = flow.run_local_server(port=0)
  # Save the credentials for the next run
  with open("token.json", "w") as token:
    token.write(creds.to_json())

# Call the Gmail API
service = build("gmail", "v1", credentials=creds)
results = (
    service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
)
messages = results.get("messages", [])

if not messages:
    print("No messages found.")

print("Messages:")
for message in messages:
    print(f'Message ID: {message["id"]}')
    msg = (
        service.users().messages().get(userId="me", id=message["id"]).execute()
    )
    print(f'  Subject: {msg["snippet"]}')

# To add: pagination. See below from documentation
""""
The messages.list method returns a response body that contains the following:

    messages[]: An array of Message resources.
    nextPageToken: For requests with multiple pages of results, a token that can be used with subsequent calls to list more messages.
    resultSizeEstimate: An estimated total number of results.

To fetch the full message content and metadata, use the message.id field to call the messages.get method.

from: https://developers.google.com/workspace/gmail/api/guides/list-messages?_gl=1*1y3jpvq*_up*MQ..*_ga*MTUwMTAzOTYxMS4xNzkwMzUzMzkz*_ga_SM8HXJ53K2*czE3OTAzNTMzOTMkbzEkZzAkdDE3OTAzNTMzOTMkajYwJGwwJGgw
"""