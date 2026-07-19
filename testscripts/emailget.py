import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Authenticate with OAuth 2.0 (requires user consent)
creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/contacts.readonly'])
service = build('people', 'v1', credentials=creds)

# Search for contacts by phone number
phone_number = '+918118069448'  # Replace with the number
results = service.people().connections().list(
    resourceName='people/me',
    personFields='emailAddresses,phoneNumbers',
    pageSize=1000
).execute()

# Check if the phone number exists in your contacts
for person in results.get('connections', []):
    for number in person.get('phoneNumbers', []):
        if number.get('value') == phone_number:
            print(f"Name: {person.get('names', [{}])[0].get('displayName')}")
            print(f"Email: {person.get('emailAddresses', [{}])[0].get('value')}")
