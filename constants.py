CREDENTIALS_FILE_PATH = './secrets/credentials.json'
GOOGLE_SERVICES = {
    'gmail': 'gmail',
}
LABELS_FILE_PATH = './secrets/labels.json'
PROCESSED_MESSAGES_FILE_PATH = './secrets/processed-messages.json'
MAX_MESSAGE_RESULTS = 500
SCOPES = {
    # https://mail.google.com/
    'compose': 'https://www.googleapis.com/auth/gmail.compose',
    'metadata': 'https://www.googleapis.com/auth/gmail.metadata',
    'modify': 'https://www.googleapis.com/auth/gmail.modify',
    'readonly': 'https://www.googleapis.com/auth/gmail.readonly',
}
SELECTORS = {
    # DiDi
    'Label_3079202437021194369': {
        'amount': 'body > table > tbody > tr > td > div.root-container > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr > td > table > tbody > tr > td > table:nth-child(1) > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > table > tbody > tr:nth-child(1) > td:nth-child(2) > table > tbody > tr:nth-child(2) > td:nth-child(2)',
        'date': 'body > table > tbody > tr > td > div.root-container > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table:nth-child(1) > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > div > table > tbody > tr > td > table > tbody > tr:nth-child(2) > td:nth-child(2) > span',
        'time': 'body > table > tbody > tr > td > div.root-container > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > div > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr:nth-child(3) > td:nth-child(2) > table > tr > td:nth-child(2) > table > tr > td:nth-child(1) > div:nth-child(1) > strong > span:nth-child(1)',
        'time2': 'body > table > tbody > tr > td > div.root-container > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > div > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr:nth-child(3) > td:nth-child(2) > table > tr > td:nth-child(2) > table > tr > td:nth-child(1) > div:nth-child(1) > strong > span:nth-child(1)',
        'comments': 'body > table > tbody > tr > td > div.root-container > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr > td > table > tbody > tr > td > table:nth-child(2) > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > table > tbody > tr > td > div > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody > tr:nth-child(3) > td:nth-child(2) > table > tr > td:nth-child(2) > table > tr > td:nth-child(1) > div:nth-child(2) > span'
    }
}
TOKEN_FILE_PATH = './secrets/token.json'

QUERIES = {
    'label:promotions or category:promotions after:2025/12/31',
    'label:social or category:social after:2025/12/31',
    'after:2026/01/31 before:2026/02/28 subject:("your express trip" OR "your set your fare trip" OR "your cancelled express trip")',
    'after:2025/12/31 before:2026/02/01 subject:("your express trip" OR "your set your fare trip" OR "your cancelled express trip")',
    'after:2025/11/30 before:2026/01/01 subject:("your express trip" OR "your set your fare trip" OR "your cancelled express trip")'
    'after:2025/10/31 before:2025/12/01 subject:("your express trip" OR "your set your fare trip" OR "your cancelled express trip")'
    'after:2025/09/30 before:2025/11/01 subject:("your express trip" OR "your set your fare trip" OR "your cancelled express trip")'
}