import sys
import time
import urllib.parse
import unittest

import database
from mitmproxy import http as mitm_http
from mitmproxy import ctx
import os

sync_interval = int(os.environ.get('sync_interval')) if os.environ.get('sync_interval') is not None else 10
db_name = os.environ.get("db_name") or ":memory:"
mode = os.environ.get("mode") or "prod"


class Blocker:
    def __init__(self, should_log):
        self.db = database.Database(db_name)
        self.blocked = self.db.read_blocked()
        self.browsed = set()
        self.last_updated = time.time()
        self.should_log = should_log
        self.log_blocked()

    def request(self, flow):
        if next(filter(lambda url: url in flow.request.pretty_url, self.blocked), None):
            flow.response = mitm_http.Response.make(404, b"How about studying", {"Content-Type": "text/html"})
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




def should_update(last_updated):
    minutes = (time.time() - last_updated) / 60
    if minutes > sync_interval:
        return True
    return False


# tests
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
    ctx.log.info("Must set environment variable 'db_name' and it should not be set to ':memory:' for 'prod' mode")
    should_exit = True
if should_exit:
    sys.exit("Missing environment variable for DB")

addons = [
    Blocker(mode_prod) if mode_prod else None
]

if __name__ == '__main__':
    unittest.main()
