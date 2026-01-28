def gmail_user_messages_list(
    service: object,
    search_query: str = "",
    max_results: int = 5,
    label_ids: list = None
) -> list:
    """Fetches a list of user messages from Gmail.

    Args:
        service: The authenticated Gmail API service instance.
        max_results: Maximum number of messages to retrieve.
        label_ids: List of label IDs to filter messages.
        search_query: Query string to filter messages. Supports the same advanced search syntax as the Gmail web interface.
    Returns:    
        A list of message objects.
    """
    messages_res = service.users().messages().list(
        userId='me',
        maxResults=max_results,
        labelIds=label_ids,
        q=search_query
    ).execute()
    messages = messages_res.get('messages', [])
    return messages

def gmail_user_messages_get(
    service: object,
    userId: str,
    id: str = "",
    format: str = "full"
) -> object:
    """Fetches a user message from Gmail.

    Args:
        service: The authenticated Gmail API service instance.
        userId: The user ID to retrieve messages for.
        id: The message ID to retrieve.
        format: The format of the message to retrieve.
    Returns:    
        A message object.
    """
    message = service.users().messages().get(userId=userId, id=id, format=format).execute()
    return message