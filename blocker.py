import os
import sys
import time
import urllib.parse
import unittest

from mitmproxy import http as mitm_http
from mitmproxy import ctx
import getpass
import sqlite3

CONFIG_FILE = ".config"
TABLE_BROWSED = 'browsed'
TABLE_BLOCKED = 'blocked'
TABLE_BROWSED_CREATE = f'CREATE TABLE IF NOT EXISTS {TABLE_BROWSED} ' \
                       f'(user TEXT, url_host TEXT,full_url TEXT, accessed_on INTEGER )'
TABLE_BLOCKED_CREATE = f'CREATE TABLE IF NOT EXISTS {TABLE_BLOCKED} ' \
                       f'(host TEXT)'
query_select_blocked = f'SELECT DISTINCT host FROM {TABLE_BLOCKED}'
query_insert_many = f'INSERT INTO {TABLE_BROWSED} VALUES (?, ?, ?, ?)'

sync_interval = int(os.environ.get('sync_interval')) if os.environ.get('sync_interval') is not None else 10
db_name = os.environ.get("db_name") or ":memory:"
mode = os.environ.get("mode") or "prod"
user = getpass.getuser()


class Blocker:
    def __init__(self, should_log):
        self.db = Database()
        self.blocked = self.db.read_blocked()
        self.browsed = set()
        self.last_updated = time.time()
        self.should_log = should_log
        self.log_blocked()

    def request(self, flow):
        if next(filter(lambda url: url in flow.request.pretty_url, self.blocked), None):
            flow.response = mitm_http.HTTPResponse.make(404, b"How about studying", {"Content-Type": "text/html"})
        else:
            self.browsed.add(flow.request.pretty_url)
        if should_update(self.last_updated):
            self.do_update()

    def done(self):
        self.db.close()

    def log_blocked(self):
        if self.should_log:
            ctx.log.info("Blocked host names are: %s" % str(self.blocked))

    def do_update(self):
        self.db.write_browsed(self.browsed)
        self.browsed = set()
        self.blocked = self.db.read_blocked()
        self.last_updated = time.time()


class Database:
    def __init__(self):
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

    def write_browsed(self, browsed_urls):
        to_insert = map(lambda r: (r.user, r.host, r.url, r.accessed_on),
                        filter(lambda x: x is not None, list(map(to_record, browsed_urls))))
        cursor = self.db.cursor()
        cursor.executemany(query_insert_many, to_insert)
        self.db.commit()
        cursor.close()

    # For testing
    def read_browsed(self):
        cursor = self.db.cursor()
        result = []
        cursor.execute(f'SELECT distinct url_host from {TABLE_BROWSED}')
        for row in cursor:
            result.append(row)
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


class BlockedRecord:
    def __init__(self, user_name, host, url, accessed_on):
        self.user = user_name
        self.host = host
        self.url = url
        self.accessed_on = accessed_on


def to_record(url):
    if url is None:
        return None
    host = urllib.parse.urlparse(url).netloc
    if host == '':
        return None
    return BlockedRecord(user, host, url, time.time())


def should_update(last_updated):
    minutes = (time.time() - last_updated) / 60
    if minutes > sync_interval:
        return True
    return False


# tests
class TestToRecord(unittest.TestCase):
    def test_to_record(self):
        cases = [
            ["https://www.mrnakumar.com", True, "www.mrnakumar.com"],
            ["https://mrnakumar.com", True, "mrnakumar.com"],
            ["https://m.youtube.com", True, "m.youtube.com"],
            ["https://dev.twitter.com", True, "dev.twitter.com"],
            ["https:///www.mrnakumar.com", False, "www.mrnakumar.com"],
            ["", False, ""],
            [None, False, None]
        ]
        for url, success, host in cases:
            result = to_record(url)
            if success is False:
                self.assertIsNone(result)
            else:
                self.assertEqual(result.host, host)
                self.assertEqual(result.url, url)


class TestDBReadWrite(unittest.TestCase):
    def test_db_read_write(self):
        db = Database()
        try:
            db.write_browsed(["https://youtube.com", "https://twitter.com"])
            result = db.read_browsed()
            self.assertListEqual(list(map(lambda r: r[0], result)), ["youtube.com", "twitter.com"])
        finally:
            db.close()


# Export plugin
should_exit = False
mode_prod = mode == "prod"
if mode_prod and db_name == ":memory:":
    ctx.log.info("Must set environment variable 'db_name'")
    should_exit = True
if should_exit:
    sys.exit("Missing environment variables for DB")

addons = [
    Blocker(mode_prod) if mode_prod else None
]

if __name__ == '__main__':
    unittest.main()
