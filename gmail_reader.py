from gmail_users_messages import gmail_user_messages_list, gmail_user_messages_get
from google_apis import authenticate_and_build_google_service
from constants import GOOGLE_SERVICES, SCOPES, CREDENTIALS_FILE_PATH, TOKEN_FILE_PATH, LABELS_FILE_PATH
import json

def main() -> None:
    labels = json.load(open(LABELS_FILE_PATH))
    labels_dict = {label['name']: label['id'] for label in labels}
    # print("Available Labels:", labels_dict["my_label"], labels_dict.get("my_label", "Label not found"))
    service = authenticate_and_build_google_service(
        service_name=GOOGLE_SERVICES['gmail'],
        scopes=[SCOPES['readonly']],
        version='v1',
        credentials_file=CREDENTIALS_FILE_PATH,
        token_file=TOKEN_FILE_PATH,
    )
    messages = gmail_user_messages_list(
        service=service,
        max_results=5,
        # label_ids=["Label_xxxx"],
        search_query="subject:Your Express Trip",
    )
    for msg in messages:
        # 3. Obtener el contenido específico de cada mensaje
        message = gmail_user_messages_get(
            service=service,
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
    
    
if __name__ == '__main__':
    main()