import json
from google_apis import GoogleApis
from gmail_users import GmailUsers
from constants import GOOGLE_SERVICES, SCOPES, CREDENTIALS_FILE_PATH, TOKEN_FILE_PATH, LABELS_FILE_PATH
from utils import Utils

def main() -> None:
    labels = json.load(open(LABELS_FILE_PATH))
    labels_dict = {label['name']: label['id'] for label in labels}
    #print("Available Labels:", labels_dict["DiDi"], labels_dict.get("DiDi", "Label not found"))
    service = GoogleApis.authenticate_and_build_google_service(
        service_name=GOOGLE_SERVICES['gmail'],
        scopes=[SCOPES['readonly']],
        version='v1',
        credentials_file=CREDENTIALS_FILE_PATH,
        token_file=TOKEN_FILE_PATH,
    )
    messages = GmailUsers(service).messages
    messages_list = messages.list(
        max_results=100000,
        #label_ids=[labels_dict["DiDi"]],
        search_query="subject:Your Express Trip",
    )
    
    print(f"Found {len(messages_list)} messages matching the criteria.")
    return
    for msg in messages_list:
        # 3. Obtener el contenido específico de cada mensaje
        message = messages.get(
            userId='me',
            id=msg['id'],
            format='full'
        )
        snippet = message['snippet'] # Resumen del cuerpo
        print(f"\nID: {msg['id']}\nResumen: {snippet}")
    
        # Step 3: Extract the subject from headers
        headers = message['payload']['headers']
        for header in headers:
            if header['name'] == 'Subject':
                # Optional: verify the subject matches exactly if needed
                print(f"Subject: {header['value']}")
                # found_messages.append({'id': msg_id, 'subject': header['value'], 'full_message': msg})
                # break

def write_labels_to_json_file(print_labels: bool = False) -> None:
    service = GoogleApis.authenticate_and_build_google_service(
        service_name=GOOGLE_SERVICES['gmail'],
        scopes=[SCOPES['readonly']],
        version='v1',
        credentials_file=CREDENTIALS_FILE_PATH,
        token_file=TOKEN_FILE_PATH,
    )
    labels = GmailUsers(service).labels.list(sort_order='type', userId='me')
    if print_labels:
        print("Labels:", labels)
    Utils.write_json_file(labels, LABELS_FILE_PATH)
    
if __name__ == '__main__':
    main()