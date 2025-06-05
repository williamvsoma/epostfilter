import epostfilter.config as cfg
from epostfilter.llm_classifier import spam_classifier
from epostfilter.authenticate import authenticate
import base64
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup

def html_to_text(html_str: str) -> str:
    '''
    Convert raw HTML to plain text using BeautifulSoup.
    '''
    soup = BeautifulSoup(html_str, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def get_text_from_payload(payload) -> str:
    mime_type = payload.get('mimeType', '')
    body = payload.get('body', {})
    text = ''
    
    if mime_type == 'text/plain':
        data = body.get('data')
        if data:
            decoded_bytes = base64.urlsafe_b64decode(data)
            text = decoded_bytes.decode('utf-8', errors='replace')
            return text
        
    elif mime_type == 'text/html':
        data = body.get('data')
        if data:
            decoded_bytes = base64.urlsafe_b64decode(data)
            html_str = decoded_bytes.decode('utf-8', errors='replace')
            text = html_to_text(html_str)
        return text
    
    elif mime_type.startswith("multipart"):
        for part in payload.get('parts', []):
            text += get_text_from_payload(part)
    
    return text
    
def main() -> None:
    creds = authenticate()

    try:
        service = build("gmail", "v1", credentials=creds)
        response = service.users().messages().list(userId="me", q=cfg.query).execute()
        messages = response.get("messages", [])
        while "nextPageToken" in response:
            page_token = response["nextPageToken"]
            response = service.users().messages().list(userId="me", q=cfg.query, pageToken=page_token).execute()
            messages.extend(response.get("messages", []))
            
        if not messages:
            print("No emails found in the last 24 hours in your Inbox.")
            return None
        print(f"Total messages found in the last 24 hours: {len(messages)}\n")

        for msg in messages:
            msg_id = msg['id']
            full_message = (
                service.users().messages().get(userId="me", id=msg_id, format="full").execute()
            )
            payload = full_message.get('payload', {})
            text = get_text_from_payload(payload)
            is_spam = spam_classifier(text) 
            print(is_spam)
            if is_spam:
                service.users().messages().modify(
                    userId="me", 
                    id=msg_id, 
                    body={
                        'addLabelIds': ['SPAM'],
                        'removeLabelIds': ['INBOX'],
                    }
                ).execute()
                print(f'Email {msg_id} labeled as SPAM.')
        
    except HttpError as error:
        print(f"An error occurred: {error}") 
    return None

if __name__ == "__main__":
    main()