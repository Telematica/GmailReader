CREDENTIALS_FILE_PATH = './secrets/credentials.json'
LABELS_FILE_PATH = './secrets/labels.json'
SCOPES = {
    # https://mail.google.com/
    'compose': 'https://www.googleapis.com/auth/gmail.compose',
    'metadata': 'https://www.googleapis.com/auth/gmail.metadata',
    'modify': 'https://www.googleapis.com/auth/gmail.modify',
    'readonly': 'https://www.googleapis.com/auth/gmail.readonly',
}
GOOGLE_SERVICES = {
    'gmail': 'gmail',
}
TOKEN_FILE_PATH = './secrets/token.json'
