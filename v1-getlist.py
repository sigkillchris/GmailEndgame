#! usr/bin/env python3

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
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
    queryString = 'before:2012/01/01 and after:2011/01/01 and label:unread'
    queryTest = 'after: 2020/05/05'
    PrintEmailCount(service, queryTest)

    print('Checking for messages matching %s...' % queryTest)

    #print gmail list API
    #messages = ListMessagesMatchingQuery(service, ME, queryString)
    messagesIDs = ListMessagesMatchingQuery(service, ME, queryTest)

    #print(messagesIDs)
    raw_messages = prep_messages_for_delete(ListMessagesMatchingQuery(service, ME, queryTest))

    messagesList = GetMessageIDs(raw_messages)
    print(messagesList)
    idList = prep_messages_for_delete(messagesList)
    print(idList)

    #batch_delete_messages(service, messagesList)



    print('job completed')


#need to make a get credentions function

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

def GetMessageIDs(raw_messages):
    ids = []

    if not raw_messages:
        print('No Messages found.')
    else:
        for message in raw_messages:
            ids.append(message['id'])
        print(ids)
    return ids

def prep_messages_for_delete(ids):
    prepMessage = {
        'ids': []
    }

    prepMessage['ids'].extend(ids)

    return prepMessage

def batch_delete_messages(service, messages):
    print("ready to delete {} messages".format(len(messages['ids'])))
    user_id = "me"

    try:
        service.users().messages().batchDelete(
            userId=user_id,
            body=messages
        ).execute()

        print("I deleted stuff!")
    except errors.HttpError as error:
        print('An error occurred while batchDeleting: {0}'.format(error))

if __name__ == '__main__':
    main()
