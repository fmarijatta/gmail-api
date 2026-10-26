import os.path
import base64
import re
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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

  #Define parsing variables
  url_regex = re.compile(r"\(https:\/\/archiveofourown.org\/works\/\d+\).", re.IGNORECASE)

  try:
      # Call the Gmail API
      service = build("gmail", "v1", credentials=creds)
      results = (
          service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
      )
      messages = results.get("messages", [])

      if not messages:
          print("No messages found.")
          return
      for message in messages:
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

          #Regex to extract key info from message body. Will be converted to a function later!
          body_main = re.split('[=]+', body)[1] # remove email title
          body_trim = re.split('-{40,}', body_main)[0] # trim trailing dashes at the end of the body text
          body_list = re.split('-{10,}', body_trim) #remove new-line dividers (----)
          for item in body_list:
            body_clean = re.sub(url_regex, '', item.strip()).strip() #trim spaces and remove url string
            metrics, title = re.split(' left kudos on ', body_clean)
            title = title.strip('"')
            print(title)
            print(metrics)

            #Identify number of guest kudos
            guest_match = re.search('[Aa\d]+\sguests?$', metrics)
            if guest_match:
              guests = guest_match.group()
              n_guests = re.sub('\sguests?', '', guests)
              n_guests = n_guests if n_guests.lower() != 'a' else 1
              metrics = metrics.replace(guests, '')
              and_match = re.search(',?\sand', metrics)
              if and_match:
                metrics = metrics.replace(and_match.group(), '').strip()
            else:
              n_guests = 0

            # Identify number of user kudos
            if len(metrics) == 0:
              n_users = 0
            else:
              users = metrics.replace(',', '').replace(' and ', ' ')
              n_users = users.count(' ') + 1
            
            # Check output
            print(f'Number of users: {n_users}')
            print(f'Number of guests: {n_guests}')
            print('\n')

          # TO DO:
          ## Extract date of email
          ## Store in pandas df? Can then append
          ## Pagination!!
          break

  except HttpError as error:
      # TODO(developer) - Handle errors from gmail API.
      print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()