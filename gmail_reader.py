from ast import arg
from datetime import datetime
import json
from math import exp
import re
from bs4 import BeautifulSoup
from google_apis import GoogleApis
from gmail_users import GmailUsers
from constants import ES_TO_EN_MONTHS, GOOGLE_SERVICES, LABELS_FILE_PATH, PROCESSED_MESSAGES_FILE_PATH, SCOPES, CREDENTIALS_FILE_PATH, TOKEN_FILE_PATH, MAX_MESSAGE_RESULTS, SELECTORS
from utils import Utils
from datetime import date, timedelta
import sys

def main() -> None:
    arguments = sys.argv[1:]  # Get command-line arguments excluding the script name
    
    if "--all" in arguments:
        count_inbox_unread_messages()
        return
    
    if "--today" in arguments:
        count_daily_received_unread_messages()
        return

    if "--rappi" in arguments:
        labels_dict = {label["name"]: label["id"] for label in Utils.load_json_file(
            file_path=LABELS_FILE_PATH)}  # dictionary comprehension
        scrap_rappi_label(
            search_query='after:1767247199 before:1798783200',
            label_ids=[labels_dict.get("Rappi/Pedidos")],
            mark_as_read_emails=False,
            print_json_output=False
        )
    
    # scrap_didi_label(
    #   search_query='after:1756706399 before:1759298400 subject:("your express trip" OR "your set your fare trip" OR "your cancelled express trip")'
    #   label_ids=[labels_dict.get("DiDi")]
    # )
    # export_message_html_to_file_by_message_id(
    #     file_path='./email-templates/rappi-corner-case-2025.html',
    #     message_id="<message_id_here>"
    # )
    # write_labels_to_json_file()
    # print(
    #    Utils.get_time_zoned_epoch_datetime('2025/12/31 23:59:59'),
    #    Utils.get_time_zoned_epoch_datetime('2027/01/01 00:00:00')
    # )
    
def count_daily_received_unread_messages() -> None:
    service = GoogleApis.authenticate_and_build_google_service(
        service_name=GOOGLE_SERVICES['gmail'],
        scopes=[SCOPES["modify"], SCOPES["readonly"]],
        version='v1',
        credentials_file=CREDENTIALS_FILE_PATH,
        token_file=TOKEN_FILE_PATH,
    )
    messages = GmailUsers(service).messages
    page_token = '0'
    total_messages = 0
    total_messages_unread = 0
    today = date.today().strftime('%Y/%m/%d')
    tomorrow = (date.today() + timedelta(days=1)).strftime('%Y/%m/%d')
    yesterday = (date.today() - timedelta(days=1)).strftime('%Y/%m/%d')
    yesterday = str(Utils.get_time_zoned_epoch_datetime(f'{yesterday} 23:59:59')).replace(".0", "")
    tomorrow = str(Utils.get_time_zoned_epoch_datetime(f'{tomorrow} 00:00:00')).replace(".0", "")

    while page_token is not None:
        response = messages.list(
            search_query=f'after:{yesterday} before:{tomorrow}', # label:(INBOX AND UNREAD)
            label_ids=['INBOX', 'UNREAD'],
            max_results=MAX_MESSAGE_RESULTS,
            pageToken=page_token
        )
        messages_list = response.get('messages', [])
        total_messages_unread += len(messages_list)
        page_token = response.get('nextPageToken', None)
        # print("Next Page Token:", page_token)
        # print("Messages:", messages_list)
        # print("Number of messages found (partial batch):", len(messages_list))
    
    page_token = '0'
    
    while page_token is not None:
        response = messages.list(
            search_query=f'after:{yesterday} before:{tomorrow}', # label:(INBOX AND UNREAD)
            # label_ids=['INBOX'],
            max_results=MAX_MESSAGE_RESULTS,
            pageToken=page_token
        )
        messages_list = response.get('messages', [])
        total_messages += len(messages_list)
        page_token = response.get('nextPageToken', None)

    print("Total messages received today", today, ":", total_messages)
    print("Total unread messages received today", today, ":", total_messages_unread)

def count_inbox_unread_messages() -> None:
    service = GoogleApis.authenticate_and_build_google_service(
        service_name=GOOGLE_SERVICES['gmail'],
        scopes=[SCOPES["readonly"]],
        version='v1',
        credentials_file=CREDENTIALS_FILE_PATH,
        token_file=TOKEN_FILE_PATH,
    )
    messages = GmailUsers(service).messages
    page_token = None
    total_messages = 0
    
    while page_token is not None or total_messages == 0:
        response = messages.list(
            # search_query='label:(INBOX AND UNREAD)',
            label_ids=['INBOX', 'UNREAD'],
            max_results=MAX_MESSAGE_RESULTS,
            pageToken=page_token
        )
        messages_list = response.get('messages', [])
        total_messages += len(messages_list)
        page_token = response.get('nextPageToken', None)
        print("Next Page Token:", page_token)
        print("Number of messages found (partial batch):", len(messages_list))
    print("Total unread messages in INBOX:", total_messages)

def scrap_rappi_label(
    search_query: str,
    label_ids: list = None,
    mark_as_read_emails: bool = False,
    print_json_output: bool = False,
    print_message_log: bool = False
) -> None:
    # Get the Gmail service instance
    service = GoogleApis.authenticate_and_build_google_service(
        service_name=GOOGLE_SERVICES['gmail'],
        scopes=[SCOPES["modify"], SCOPES["readonly"]],
        version='v1',
        credentials_file=CREDENTIALS_FILE_PATH,
        token_file=TOKEN_FILE_PATH,
    )
    messages = GmailUsers(service).messages
    json_items = []
    messages_list = []
    message_ids = []
    page_token = None
    total_messages = 0
    skipped_messages = 0

    while page_token is not None or total_messages == 0:
        msgs_temp = messages.list(
            max_results=MAX_MESSAGE_RESULTS,
            label_ids=label_ids,
            search_query=search_query,
            pageToken=page_token
        )
        messages_list = [*messages_list, *msgs_temp.get('messages', [])]
        page_token = msgs_temp.get('nextPageToken')
        total_messages += len(msgs_temp.get('messages', []))
        message_ids = [message["id"] for message in messages_list]
        print("Next Page Token:", page_token)
        print("Number of messages found (partial batch):",
              len(msgs_temp.get('messages', [])))

    print("Total messages found:", total_messages)

    for msg in messages_list:
        print("Message ID:", msg['id'])
        message = messages.get(
            userId='me',
            id=msg['id'],
            format='full'
        )
        # snippet = message['snippet'] # Resumen del cuerpo

        # Extract the subject from headers
        subject: str = None
        header_date: str = None
        headers: list = message['payload']['headers']
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'Date':
                header_date = header['value']

        # @TODO: If message['payload'].get("parts"), iterate all parts otherwise get payload.body directly
        html_content = message['payload'].get("parts")[0].get("body", {}).get("data", '').encode(
            'UTF8') if message['payload'].get("parts") else message['payload'].get('body', {}).get('data', '').encode('UTF8')
        soup: BeautifulSoup = Utils.get_html_document(html_content)

        # Step []: Scrap HTML Document using selectors to find data
        selector_express = SELECTORS['Label_431']['express']
        selector_normal = SELECTORS['Label_431']['normal']
        selector_corner_case_2025 = SELECTORS['Label_431']['corner_case_2025']
        amount = soup.select(
            selector_express['amount'] + ',' + selector_normal["amount"])

        if len(amount) == 0 and "ha sido cancelado" in subject:
            print(f"Mensaje de Pedido Cancelado, no se procesará: {msg['id']}")
            skipped_messages += 1
            continue
        elif "Ya puedes ver tu factura Turbo" == subject:
            print(f"Mensaje de Factura Turbo, omitido: {msg['id']}")
            skipped_messages += 1
            continue
        elif len(amount) == 0:
            print(
                f"Mensaje no contiene los datos requeridos, no se procesará: {msg['id']}")
            skipped_messages += 1
            continue

        def replacer(match) -> str:
            word = ES_TO_EN_MONTHS[match.group(0)]
            return word
        regex = "|".join(ES_TO_EN_MONTHS.keys())
        header_date_year = Utils.get_year_from_date(header_date)

        amount = amount[0].text.strip()
        date = soup.select(
            selector_express['date'] + ',' + selector_normal["date"] + ',' + selector_corner_case_2025["date"])[0].text.strip()
        date = datetime.strptime(re.sub(regex, replacer, date.replace(
            ".", f" {header_date_year}").strip()), "%d %B %Y %I:%M %p") if "." in date else date
        comments1 = soup.select(selector_normal['comments1'])[0].text.strip()
        comments2 = soup.select(selector_normal['comments2'])[0].text.strip()
        bank = 'Banregio' # @TODO: Extract bank from comments or other data in the email, currently hardcoded as Banregio for all transactions
        mean_of_payment = 'Tarjeta de Crédito' # @TODO: Extract mean of payment from comments or other data in the email, currently hardcoded as Tarjeta de Crédito for all transactions

        if print_message_log:
            print("Amount:", amount)
            print("Date header:", header_date)
            print("Comments1:", comments1)
            print("Comments2:", comments2)
            print("GmailMessageId:", msg['id'] + "\n")

        json_items.append({
            'Monto': float(amount.replace('$', '').replace(',', '').strip()),
            'Currency': 'MXN',
            'Impuestos': None,
            'Medio': mean_of_payment,
            'Banco': bank,
            'DateTime': Utils.format_date_string(f'{date}', '%m/%d/%Y %H:%M:%S'),
            'Concepto': 'Rappi',
            'Type': 'food',
            'Comments': [
                f"{header_date}",
                f"{comments1}",
                f"{comments2}",
            ],
            "GmailMessageId": msg['id']
        })

    print("Total messages skipped:", skipped_messages)
    print("Total messages processed:", len(json_items))

    if print_json_output:
        print(json.dumps(json_items, indent=None, separators=(', ', ': ')))

    json_string = sorted(
        json_items,
        key=lambda obj: datetime.strptime(
            obj['DateTime'], '%m/%d/%Y %H:%M:%S'),
        reverse=False
    )
    json_string = json.dumps(json_string, indent=None, separators=(', ', ': '))
    Utils.write_json_file(json_str=json_string,
                          filename='./secrets/most-recent-query.json')
    Utils.copy_to_clipboard(json_string)

    # Last Step []: Mark processed emails as Read and remove from Inbox
    if mark_as_read_emails:
        messages.batchModify(
            add_label_ids=["Label_3919000443246267002"],
            message_ids=message_ids,
            remove_label_ids=["INBOX", "UNREAD"],
            userId='me',
        )


def scrap_didi_label(search_query: str, label_ids: list = None) -> None:
    # Step [1]: Get the Google API Gmail service instance
    service = GoogleApis.authenticate_and_build_google_service(
        service_name=GOOGLE_SERVICES['gmail'],
        scopes=[SCOPES["modify"], SCOPES["readonly"]],
        version='v1',
        credentials_file=CREDENTIALS_FILE_PATH,
        token_file=TOKEN_FILE_PATH,
    )

    pageToken = None
    totalMessages = 0
    messages_list = []
    messages = GmailUsers(service).messages

    # Step [2]: Fetch messages based on criteria (search_query and labels_ids)
    while pageToken is not None or totalMessages == 0:
        msgs_temp = messages.list(
            max_results=MAX_MESSAGE_RESULTS,
            label_ids=label_ids,
            search_query=search_query,
            pageToken=pageToken
        )
        messages_list = [*messages_list, *msgs_temp.get('messages', [])]
        pageToken = msgs_temp.get('nextPageToken')
        totalMessages += len(msgs_temp.get('messages', []))
        message_ids = [message["id"] for message in messages_list]
        print("Next Page Token:", pageToken)
        print("Number of messages found (partial batch):",
              len(msgs_temp.get('messages', [])))

    print("Total messages found:", totalMessages)
    print("Processing messages...", messages_list)

    # Step [3]: Mark processed emails as Read and remove from Inbox
    messages.batchModify(
        userId='me',
        body={
            # A list of label IDs to remove from messages.
            "removeLabelIds": ["INBOX", "UNREAD"],
            # The IDs of the messages to modify. There is a limit of 1000 ids per request.
            "ids": message_ids,
            "addLabelIds": [  # A list of label IDs to add to messages.
                "Label_3919000443246267002",
            ],
        }
    ).execute()

    # Step [4]: Save processed emails ids to file
    # @TODO: Manage with a DB instead
    write_processed_messages_ids_to_json_file(message_ids)

    json_items = []
    for msg in messages_list:
        print("Message ID:", msg['id'])
        message = messages.get(
            userId='me',
            id=msg['id'],
            format='full'
        )
        # snippet = message['snippet'] # Resumen del cuerpo

        # Extract the subject from headers
        subject: str = None
        headers: list = message['payload']['headers']
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
                break

        # @TODO: If message['payload'].get("parts"), iterate all parts otherwise get payload.body directly
        html_content = message['payload'].get("parts")[0].get("body", {}).get("data", '').encode(
            'UTF8') if message['payload'].get("parts") else message['payload'].get('body', {}).get('data', '').encode('UTF8')
        soup: BeautifulSoup = Utils.get_html_document(html_content)

        # Step []: Scrap HTML Document using selectors to find data
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
        key=lambda obj: datetime.strptime(
            obj['DateTime'], '%m/%d/%Y %H:%M:%S'),
        reverse=False
    )
    json_string = json.dumps(json_string, indent=None, separators=(', ', ': '))
    Utils.write_json_file(json_str=json_string,
                          filename='./secrets/most-recent-query.json')
    Utils.copy_to_clipboard(json_string)
    
def export_message_html_to_file_by_message_id(file_path: str, message_id: str) -> None:
    service = GoogleApis.authenticate_and_build_google_service(
        service_name=GOOGLE_SERVICES['gmail'],
        scopes=[SCOPES['readonly']],
        version='v1',
        credentials_file=CREDENTIALS_FILE_PATH,
        token_file=TOKEN_FILE_PATH,
    )
    message = service.users().messages().get(
        userId="me",
        id=message_id,
        format="full"
    ).execute()
    html_content = message['payload'].get("parts")[0].get("body", {}).get("data", '').encode('UTF8') if message['payload'].get("parts") else message['payload'].get('body', {}).get('data', '').encode('UTF8')
    soup: BeautifulSoup = Utils.get_html_document(html_content)
    Utils.export_html_to_file(file_path=file_path, html_content=html_content)
    print(f"HTML content of message with ID {message_id} has been exported to {file_path}")


def write_labels_to_json_file(
    print_labels: bool = False,
    sort_order: str = 'type',
    userId: str = 'me'
) -> None:
    """
    Write User Labels to JSON file

    :param print_labels: Print output
    :type print_labels: bool
    :param sort_order: JSON file item sorting criteria
    :type sort_order: str
    :param userId: Gmail User Id
    :type userId: str
    """
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
    """
    Write processed Message Ids to JSON file

    :param ids: Message Ids list/set
    :type ids: set | list
    :param print_ids: Print output
    :type print_ids: bool
    """
    if print_ids:
        print("IDs:", ids)
    stored_ids = json.load(open(PROCESSED_MESSAGES_FILE_PATH))
    Utils.write_json_file(
        list({*stored_ids, *ids}), PROCESSED_MESSAGES_FILE_PATH)


if __name__ == '__main__':
    main()
