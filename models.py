class BlockedRecord:
    def __init__(self, user_name, host, url, accessed_on):
        self.user = user_name
        self.host = host
        self.url = url
        self.accessed_on = accessed_on
