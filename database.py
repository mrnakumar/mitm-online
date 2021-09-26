import os
import sqlite3

TABLE_BROWSED = 'browsed'
TABLE_BLOCKED = 'blocked'
TABLE_BROWSED_CREATE = f'CREATE TABLE IF NOT EXISTS {TABLE_BROWSED} ' \
                       f'(user TEXT, url_host TEXT,full_url TEXT, accessed_on INTEGER )'
TABLE_BLOCKED_CREATE = f'CREATE TABLE IF NOT EXISTS {TABLE_BLOCKED} ' \
                       f'(host TEXT)'
query_select_blocked = f'SELECT DISTINCT host FROM {TABLE_BLOCKED}'
query_insert_many = f'INSERT INTO {TABLE_BROWSED} VALUES (?, ?, ?, ?)'
execute_block_many = f'INSERT INTO {TABLE_BLOCKED} VALUES (?)'
db_name = os.environ.get("db_name") or ":memory:"


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

    def write_browsed(self, browsed_urls):
        to_insert = map(lambda r: (r.user, r.host, r.url, r.accessed_on),
                        filter(lambda x: x is not None, list(map(to_record, browsed_urls))))
        cursor = self.db.cursor()
        cursor.executemany(query_insert_many, to_insert)
        self.db.commit()
        cursor.close()

    def read_browsed(self):
        cursor = self.db.cursor()
        result = []
        cursor.execute(f'SELECT distinct url_host from {TABLE_BROWSED}')
        for row in cursor:
            result.append(row[0])
        cursor.close()
        return result

    def close(self):
        print("Closing db connection...")
        self.db.commit()
        self.db.close()
        print("Closed db connection")


    def create_tables(self):
        c = self.db.cursor()
        c.execute(TABLE_BLOCKED_CREATE)
        c.execute(TABLE_BROWSED_CREATE)
        self.db.commit()
        c.close()
