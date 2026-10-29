import os.path
import re
import base64
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build #Construct a Resource for interacting with an API.
from googleapiclient.errors import HttpError
from modules.email_parse import extract_metrics

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
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

  #Define API variables
  maxPages = 10
  maxResults = 1
  messages = []
  out = []
  pages = 1
  q_filter = "subject:([AO3] You've got kudos!)"
  
  
  #1168 currently in inbox. so should be 3 pages max
  try:
    # Build the API connection
    service = build("gmail", "v1", credentials=creds)
  except HttpError as error:
      # TODO(developer) - Handle errors from gmail API.
      print(f"An error occurred: {error}")

    #Extract first page of message IDs
  results = (
      service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=maxResults, q=q_filter).execute()
  )
  messages.extend(results.get("messages", []))
  nextPageToken = results['nextPageToken']
  while pages <= maxPages and nextPageToken != None:
    print(f'Extracting message IDs for page {pages}...')
    results = (
            service.users().messages().list(userId="me", labelIds=["INBOX"], maxResults=maxResults, pageToken = nextPageToken, q=q_filter).execute()
        )
    try:
      nextPageToken = results['nextPageToken']
    except:
      nextPageToken = None
    messages.extend(results.get("messages", []))
    pages += 1
  print(f'{len(messages)} successfully extracted.')
    

  if not messages:
      print("No messages found.")
      return
  for message in messages:
    message_id = message["id"]
    msg = (
        service.users().messages().get(userId="me", id=message["id"]).execute()
    )
    #Extract message header
    message_header = {}
    for item in msg['payload']['headers']:
        message_header.update({item['name']: item['value']})
    msg_subject = message_header['Subject']
    if msg_subject == "[AO3] You've got kudos!":
      body = base64.urlsafe_b64decode(msg['payload']['parts'][0]['body']['data']).decode()
      message_date = message_header['Date']
      out.extend(extract_metrics(body, message_id, message_date))
  print(pd.DataFrame(out))






if __name__ == "__main__":
  main()