from typing import Any, List


class GmailUsers():
    """Google API Client discovery - Resource wrapper/Namespace.
    
    Provides methods to interact with Gmail Users resources.
    """
    def __init__(self, service) -> None:
        self.service = service
        self.labels = self.Labels(self)
        self.messages = self.Messages(self)
        
    class Labels():
        """Nested class for Gmail Users Labels resource.

        Provides methods to interact with Gmail Users Labels resources.
        """
        def __init__(self, parent) -> None:
            self.parent = parent
    
        def list(
            self,
            sort_order: str = 'id',
            userId: str = 'me',
        ) -> List:
            """Fetches a list of user labels from Gmail.

            Args:
                sort_order: The order to sort labels by ('id' or 'name' or 'type').
                userId: The user ID to retrieve messages for.
            Returns:    
                A message object.
            """
            results = self.parent.service.users().labels().list(userId=userId).execute()
            labels = results.get('labels', [])
            sorted_labels = sorted(labels, key=lambda label: label[sort_order].lower())
            return sorted_labels

    class Messages():
        """Nested class for Gmail Users Messages resource.
        
        Provides methods to interact with Gmail Users Messages resources.
        """
        def __init__(self, parent) -> None:
            self.parent = parent

        def list(
            self,
            search_query: str = "",
            max_results: int = 5,
            label_ids: list = None
        ) -> List:
            """Fetches a list of user messages from Gmail.

            Args:
                service: The authenticated Gmail API service instance.
                max_results: Maximum number of messages to retrieve.
                label_ids: List of label IDs to filter messages.
                search_query: Query string to filter messages. Supports the same advanced search syntax as the Gmail web interface.
            Returns:    
                A list of message objects.
            """
            messages_res = self.parent.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                labelIds=label_ids,
                q=search_query
            ).execute()
            messages = messages_res.get('messages', [])
            return messages

        def get(
            self,
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
            message = self.parent.service.users().messages().get(
                userId=userId,
                id=id,
                format=format
            ).execute()
            return message
