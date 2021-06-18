import http.client
import os
import sys
import threading
import time
import urllib.parse
import unittest

import parameterized
from mitmproxy import http as mitm_http
from mitmproxy import ctx
import getpass
import sqlite3

CONFIG_FILE = ".config"
ACTION_ALLOW = "ALLOW"
ACTION_BLOCK = "BLOCK"
TABLE_BROWSED = 'browsed'
TABLE_BLOCKED = 'blocked'
TABLE_BROWSED_CREATE = f'CREATE TABLE IF NOT EXISTS {TABLE_BROWSED} ' \
                       f'(user TEXT, url_host TEXT,full_url TEXT, accessed_on INTEGER )'
TABLE_BLOCKED_CREATE = f'CREATE TABLE IF NOT EXISTS {TABLE_BLOCKED} ' \
                       f'(host TEXT)'

http_sync_interval = 10 * 60
blocked = []
urls = []
browsed = []
urls_active = threading.Lock()

db_name = os.environ.get("db_name") or ":memory:"
mode = os.environ.get("mode") or "prod"
user = getpass.getuser()
query_select_blocked = f'SELECT DISTINCT host FROM {TABLE_BLOCKED}'
query_insert_many = f'INSERT INTO {TABLE_BROWSED} VALUES (?, ?, ?, ?)'


class Blocker:
    def __init__(self, should_log):
        self.db = Database()
        self.rules = self.db.read_blocked()
        self.should_log = should_log
        if self.should_log:
            self.log_blocked()

    def request(self, flow):
        if next(filter(lambda url: url in flow.request.pretty_url, self.rules), None):
            flow.response = mitm_http.HTTPResponse.make(404, b"How about studying", {"Content-Type": "text/html"})

    def log_blocked(self):
        ctx.log.info("Blocked host names are: %s" % str(self.rules))


class Database:
    def __init__(self):
        self.db = sqlite3.connect(db_name)
        self.create_tables()

    def read_blocked(self):
        host_names = []
        for host in self.db.execute(query_select_blocked):
            host_names.append(host)
        return host_names

    def write_browsed(self, browsed_urls):
        to_insert = list(map(to_record, browsed_urls))
        self.db.executemany(query_insert_many, to_insert)
        self.db.commit()

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


def get_host_name(url):
    def close(self):
        self.browsed.commit()
        self.blocked.commit()
        self.browsed.close()
        self.blocked.close()


# tests
def create_db():
    blocked_db = sqlite3.connect(db_name)


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


# Export plugin
should_exit = False
mode_prod = mode is "prod"
if mode_prod and db_name is ":memory:":
    ctx.log.info("Must set environment variable 'db_name'")
    should_exit = True
if should_exit:
    sys.exit("Missing environment variables for DB")

addons = [
    Blocker(mode_prod)
]

if __name__ == '__main__':
    unittest.main()
