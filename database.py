from models import BlockedRecord
from models import User
import os
import sqlite3
import time
import urllib.parse
import getpass

TABLE_BROWSED = "browsed"
TABLE_BLOCKED = "blocked"
TABLE_IGNORED = "ignored"
TABLE_USER = "user"
TABLE_BROWSED_CREATE = (
    f"CREATE TABLE IF NOT EXISTS {TABLE_BROWSED} "
    f"(user TEXT, url_host TEXT,full_url TEXT, accessed_on INTEGER )"
)
TABLE_BLOCKED_CREATE = (
    f"CREATE TABLE IF NOT EXISTS {TABLE_BLOCKED} " f"(host TEXT, UNIQUE(host))"
)
TABLE_IGNORED_CREATE = (
    f"CREATE TABLE IF NOT EXISTS {TABLE_IGNORED} " f"(host TEXT, UNIQUE(host))"
)
TABLE_USER_CREATE = (
    f"CREATE TABLE IF NOT EXISTS {TABLE_USER} " f"(id TEXT, password TEXT)"
)
query_select_blocked = f"SELECT DISTINCT host FROM {TABLE_BLOCKED}"
query_select_ignored = f"SELECT DISTINCT host FROM {TABLE_IGNORED}"
query_insert_many = f"INSERT INTO {TABLE_BROWSED} VALUES (?, ?, ?, ?)"
execute_block_many = f"INSERT OR IGNORE INTO {TABLE_BLOCKED} VALUES (?)"
execute_unblock_many = f"DELETE FROM {TABLE_BLOCKED} WHERE host IN (?)"
execute_ignore_many = f"INSERT OR IGNORE INTO {TABLE_IGNORED} VALUES (?)"
execute_unignore_many = f"DELETE FROM {TABLE_IGNORED} WHERE host IN (?)"
query_user_count = f"SELECT COUNT(id) from {TABLE_USER}"
query_user_find = f"SELECT * from {TABLE_USER} where id = ?"
execute_create_user = f"INSERT INTO {TABLE_USER} VALUES (?, ?)"
db_name = os.environ.get("db_name") or ":memory:"
user = getpass.getuser()


class Database:
    def __init__(self, db_name):
        self.db = sqlite3.connect(db_name)
        self.create_tables()

    def read_blocked(self):
        host_names = set()
        cursor = self.db.cursor()
        cursor.execute(query_select_blocked)
        for row in cursor:
            host = row[0]
            host_names.add(host)
        cursor.close()
        return host_names

    def write_blocked(self, hostnames_to_block):
        cursor = self.db.cursor()
        values = map(lambda hostname: (hostname,), hostnames_to_block)
        cursor.executemany(execute_block_many, values)
        self.db.commit()
        cursor.close()

    def unblock(self, hostnames):
        cursor = self.db.cursor()
        values = map(lambda hostname: (hostname,), hostnames)
        cursor.executemany(execute_unblock_many, values)
        self.db.commit()
        cursor.close()

    def read_ignored(self):
        host_names = set()
        cursor = self.db.cursor()
        cursor.execute(query_select_ignored)
        for row in cursor:
            host = row[0]
            host_names.add(host)
        cursor.close()
        return host_names

    def write_ignored(self, hostnames_to_ignore):
        cursor = self.db.cursor()
        values = map(lambda hostname: (hostname,), hostnames_to_ignore)
        cursor.executemany(execute_ignore_many, values)
        self.db.commit()
        cursor.close()

    def unignore(self, hostnames_to_unignore):
        cursor = self.db.cursor()
        values = map(lambda hostname: (hostname,), hostnames_to_unignore)
        cursor.executemany(execute_unignore_many, values)
        self.db.commit()
        cursor.close()

    def write_browsed(self, browsed_urls):
        to_insert = map(
            lambda r: (r.user, r.host, r.url, r.accessed_on),
            filter(lambda x: x is not None, list(map(self.to_record, browsed_urls))),
        )
        cursor = self.db.cursor()
        cursor.executemany(query_insert_many, to_insert)
        self.db.commit()
        cursor.close()

    def read_browsed(self):
        cursor = self.db.cursor()
        result = []
        cursor.execute(f"SELECT * from {TABLE_BROWSED}")
        for row in cursor:
            result.append(row)
        cursor.close()
        return result

    def create_user(self, user_id, password):
        cursor = self.db.cursor()
        cursor.execute(
            query_create_user,
            (
                user_id,
                password,
            ),
        )
        self.db.commit()
        cursor.close()

    def get_user_count(self):
        cursor = self.db.cursor()
        cursor.execute(query_user_count)
        count = None
        for row in cursor:
            count = row[0]
        cursor.close()
        if count is None:
            return 0
        return count

    def find_user(self, user_id):
        cursor = self.db.cursor()
        cursor.execute(query_user_find, (user_id,))
        user = None
        for row in cursor:
            user_id = row[0]
            password = row[1]
            user = User(user_id, password)
        cursor.close()
        return user

    def close(self):
        print("Closing db connection...")
        self.db.commit()
        self.db.close()
        print("Closed db connection")

    def create_tables(self):
        c = self.db.cursor()
        c.execute(TABLE_BLOCKED_CREATE)
        c.execute(TABLE_BROWSED_CREATE)
        c.execute(TABLE_IGNORED_CREATE)
        c.execute(TABLE_USER_CREATE)
        self.db.commit()
        c.close()

    def to_record(self, url):
        if url is None:
            return None
        host = urllib.parse.urlparse(url).netloc
        if host == "":
            return None
        return BlockedRecord(user, host, url, time.time())
