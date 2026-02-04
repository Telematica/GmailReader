from datetime import datetime
import json
import base64
from typing import Any
from bs4 import BeautifulSoup
from google_apis import GoogleApis
from gmail_users import GmailUsers
from constants import GOOGLE_SERVICES, SCOPES, CREDENTIALS_FILE_PATH, TOKEN_FILE_PATH, LABELS_FILE_PATH, MAX_MESSAGE_RESULTS, SELECTORS, PROCESSED_MESSAGES_FILE_PATH
from utils import Utils
from lxml import html


def main() -> None:
    scrap_didi_label()
    # write_labels_to_json_file()

def scrap_didi_label() -> None:
    # Get the Gmail service instance
    service = GoogleApis.authenticate_and_build_google_service(
        service_name=GOOGLE_SERVICES['gmail'],
        scopes=[SCOPES["modify"], SCOPES["readonly"]],
        version='v1',
        credentials_file=CREDENTIALS_FILE_PATH,
        token_file=TOKEN_FILE_PATH,
    )

    # Gmail Web compatible search query
    search_query = 'after:2025/09/30 before:2026/02/28 subject:("your express trip" OR "your set your fare trip" OR "your cancelled express trip")'
    pageToken = None
    totalMessages = 0
    messages_list = []

    while pageToken is not None or totalMessages == 0:
        # Get the Messages Resource
        messages = GmailUsers(service).messages
        msgs_temp = messages.list(
            max_results=MAX_MESSAGE_RESULTS,
            # label_ids=[labels_dict.get("DiDi")],
            search_query=search_query,
            pageToken=pageToken
        )
        messages_list = [*messages_list, *msgs_temp.get('messages', [])]
        pageToken = msgs_temp.get('nextPageToken')
        totalMessages += len(msgs_temp.get('messages', []))
        message_ids = [message["id"] for message in messages_list]
        print("Next Page Token:", pageToken)
        print("Number of messages found (partial batch):", len(msgs_temp.get('messages', [])))

    print("Total messages found:", totalMessages)
    print("Processing messages...", messages_list)
    
    service.users().messages().batchModify(
            userId='me',
            body={
                "removeLabelIds": ["INBOX", "UNREAD"], # A list of label IDs to remove from messages.
                "ids": message_ids, # The IDs of the messages to modify. There is a limit of 1000 ids per request.
                "addLabelIds": [ # A list of label IDs to add to messages.
                    "Label_3919000443246267002",
                ],
                
            }
        ).execute()
    write_processed_messages_ids_to_json_file(message_ids)
    
    json_items = []
    for msg in messages_list:
        print("Message ID:", msg['id'])
        # 3. Obtener el contenido específico de cada mensaje
        message = messages.get(
            userId='me',
            id=msg['id'],
            format='full'
        )
        # snippet = message['snippet'] # Resumen del cuerpo

        # Step 3: Extract the subject from headers
        subject: str = None
        headers: list = message['payload']['headers']
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
                break
        
        # @TODO: If message['payload'].get("parts"), iterate all parts otherwise get payload.body directly
        html_content = message['payload'].get("parts")[0].get("body", {}).get("data", '').encode('UTF8') if message['payload'].get("parts") else message['payload'].get('body', {}).get('data', '').encode('UTF8')
        soup: BeautifulSoup = get_html_document(html_content)

        # Export to HTML
        # with open('./email-templates/didi.html', "w", encoding="utf-8") as file:
        #   file.write(str(soup))
            
        selector = SELECTORS['Label_3079202437021194369']
        amount = soup.select(selector['amount'])[0].text.strip()
        date = soup.select(selector['date'])[0].text.strip()
        time = soup.select(selector['time'])[0].text.strip()
        time2 = soup.select(selector['time2'])[1].text.strip()
        comments1 = soup.select(selector['comments'])[0].text.strip()
        comments2 = soup.select(selector['comments'])[1].text.strip()
        # print("Amount:", amount)
        # print("Date:", date)
        # print("Time:", time)
        # print("Time2:", time2)
        # print("Comments1:", comments1)
        # print("Comments2:", comments2)
        # print("GmailMessageId:", msg['id'])
        json_items.append({
            'Monto': float(amount.replace('MXN$', '').replace(',', '').strip()),
            'Currency': 'MXN',
            'Impuestos': None,
            'Medio': 'Tarjeta de Crédito',
            'Banco': 'Banregio',
            'DateTime': Utils.format_date_string(f'{date} {time}', '%m/%d/%Y %H:%M:%S'),
            'Concepto': 'DiDi',
            'Type': 'transportation',
            'Comments': [
                f"Origen: {comments1} {time}",
                f"Destino: {comments2} {time2}",
                f'{"Viaje Cancelado" if subject.find("Cancelled") != -1 else "Viaje Normal"}'
            ],
            "GmailMessageId": msg['id']
        })
    print(json.dumps(json_items, indent=None, separators=(', ', ': ')))
    json_string = sorted(
        json_items,
        key=lambda obj: datetime.strptime(obj['DateTime'], '%m/%d/%Y %H:%M:%S'),
        reverse=False
    )
    json_string = json.dumps(json_string, indent=None, separators=(', ', ': '))
    Utils.write_json_file(json_str=json_string, filename='./secrets/most-recent-query.json')
    Utils.copy_to_clipboard(json_string)

def get_stored_user_labels() -> Any:
    # Load labels from JSON file
    # return dict: { "id": "CATEGORY_FORUMS", "name": "CATEGORY_FORUMS", "type": "system"},
    return json.load(open(LABELS_FILE_PATH))

def get_html_document(message: dict) -> BeautifulSoup:
    msg_str = base64.urlsafe_b64decode(message)
    soup: BeautifulSoup = BeautifulSoup(msg_str, 'lxml')
    return soup

def write_labels_to_json_file(
    print_labels: bool = False,
    sort_order: str = 'type',
    userId: str = 'me'
) -> None:
    service = GoogleApis.authenticate_and_build_google_service(
        service_name=GOOGLE_SERVICES['gmail'],
        scopes=[SCOPES['readonly']],
        version='v1',
        credentials_file=CREDENTIALS_FILE_PATH,
        token_file=TOKEN_FILE_PATH,
    )
    labels = GmailUsers(service).labels.list(sort_order, userId)
    if print_labels:
        print("Labels:", labels)
    Utils.write_json_file(labels, LABELS_FILE_PATH)
    
def write_processed_messages_ids_to_json_file(
    ids: set | list = {},
    print_ids: bool = False
) -> None:
    if print_ids:
        print("IDs:", ids)
    stored_ids = json.load(open(PROCESSED_MESSAGES_FILE_PATH))            
    Utils.write_json_file(list({*stored_ids, *ids}), PROCESSED_MESSAGES_FILE_PATH)

if __name__ == '__main__':
    main()
