class BlockedRecord:
    def __init__(self, user_name, host, url, accessed_on):
        self.user = user_name
        self.host = host
        self.url = url
        self.accessed_on = accessed_on

class User:
    def __init__(self, uid, password):
        self.id = uid
        self.password = password
        self._authenticated = uid is not None
        self._is_active = uid is not None
        self._is_anonymous = uid is None


    @property
    def is_authenticated(self):
        return self._authenticated

    @is_authenticated.setter
    def is_authenticated(self, authenticated):
        self._authenticated = authenticated

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, active):
        self._is_active = active

    @property
    def is_anonymous(self):
        return self._is_anonymous

    @is_anonymous.setter
    def is_anonymous(self, anonymous):
        self._is_anonymous = anonymous

    def get_id(self):
        # return id as unicode
        return self.id

    @staticmethod
    def load(db, user_id):
        return db.find_user(user_id)
