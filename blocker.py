import http.client
import threading
import time

from mitmproxy import http as mitm_http
from mitmproxy import ctx

import json

CONFIG_FILE = ".config"
ACTION_ALLOW = "ALLOW"
ACTION_BLOCK = "BLOCK"

http_sync_interval = 10 * 60
blocked = []
urls = []
browsed = []
urls_active = threading.Lock()


def start_http_sync():
    conn = http.client.HTTPSConnection("localhost")

    def post_periodically():
        while True:
            # TODO: add authorization header
            headers = {"Content-type": "application/json", "Accept": "application/json"}
            with urls_active:
                body = json.dumps({"urls": browsed})
                browsed.clear()

            conn.request(method="POST", url="/browsing", body=body, headers=headers)
            r = conn.getresponse()
            if r.status == 200:
                data = json.loads(r.read().decode('utf-8'))
                urls_tmp = data['urls'] if data['urls'] else []
                with urls_active:
                    urls.clear()
                    urls.extend(urls_tmp)
            time.sleep(http_sync_interval)

    syncer = threading.Thread(target=post_periodically, name='http_sync', daemon=True)
    syncer.start()


class Blocker:
    def __init__(self):
        self.rules = Blocker.read_rules()
        self.log_rules()
        start_http_sync()

    def request(self, flow):
        if next(filter(lambda url: url in flow.request.pretty_url, self.rules), None):
            flow.response = mitm_http.HTTPResponse.make(404, b"How about studying", {"Content-Type": "text/html"})

    @staticmethod
    def read_rules():
        f = open(CONFIG_FILE, "r")
        config = json.load(f)
        f.close()
        return config['urls'] if config['urls'] else []

    def log_rules(self):
        ctx.log.info("Blocked URLs are: %s" % str(self.rules))


addons = [
    Blocker()
]
