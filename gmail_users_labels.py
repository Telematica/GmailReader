def gmail_users_labels_list(
    service: object,
    sort_order: str = 'id',
    userId: str = 'me'
) -> list:
    results = service.users().labels().list(userId=userId).execute()
    labels = results.get('labels', [])
    sorted_labels = sorted(labels, key=lambda label: label[sort_order].lower())
    return sorted_labels
