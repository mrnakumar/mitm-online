from mitmproxy import http
from mitmproxy import ctx

import json

CONFIG_FILE = ".config"
ACTION_ALLOW = "ALLOW"
ACTION_BLOCK = "BLOCK"


def start_http_sync():
   pass


class Blocker:
    def __init__(self):
        self.rules = Blocker.read_rules()
        self.log_rules()
        start_http_sync()
    def request(self, flow):
        if next(filter(lambda url: url in flow.request.pretty_url, self.rules), None):
            flow.response = http.HTTPResponse.make(404, b"How about studying", {"Content-Type": "text/html"})

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
