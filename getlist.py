#! usr/bin/env python3

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from googleapiclient import errors
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://mail.google.com/']
ME = 'me'

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    #Print Email Count
    queryString = 'after: 2020/05/05'
    PrintEmailCount(service, queryString)
    print('Checking for messages matching %s...' % queryString)

    #print gmail list API
    #messages = ListMessagesMatchingQuery(service, ME, queryString)
    messagesIDs = GetMessageIDs(ListMessagesMatchingQuery(service, ME, queryString))

    print(messagesIDs)
    prepID = prep_messages_for_delete(messagesIDs)
    print(prepID)

    test = {'ids': ['12cd3e5f463ddc77']}
    print(test)
    batch_delete_messages(service, test)

    print('job completed')


def PrintEmailCount(service, queryString):
    email_count = len(ListMessagesMatchingQuery(service, ME, queryString))
    print('Email count:', email_count)

def ListMessagesMatchingQuery(service, user_id, query=''):
  """List all Messages of the user's mailbox matching the query.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

  Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except:
    print('An error occurred')


def GetMessageIDs(messages):

    messagesIDs = []
    mesID = ""
    if not messages:
        print('No Messages found.')
    else:
        for message in messages:
            messagesIDs.append(message['id'])
        #print(messagesIDs)
    return messagesIDs

def prep_messages_for_delete(ids):
    prepMessage = {
        'ids': []
    }

    prepMessage['ids'].extend(ids)

    return

def batch_delete_messages(service, messages):
    #print("ready to delete {} messages".format(len(messages['ids'])))
    user_id = "me"
    print(messages)
    try:
        service.users().messages().batchDelete(
            userId=ME,
            body=messages
        ).execute()


        print("I deleted stuff!")
    except errors.HttpError as error:
        print('An error occurred while batchDeleting: {0}'.format(error))


if __name__ == '__main__':
    main()
