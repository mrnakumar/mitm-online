from mitmproxy import http
from mitmproxy import ctx

import json

CONFIG_FILE = ".config"
ACTION_ALLOW = "ALLOW"
ACTION_BLOCK = "BLOCK"


class Blocker:
    def __init__(self):
        f = open(CONFIG_FILE, "r")
        config = json.load(f)
        f.close()
        self.rules = config['urls'] if config['urls'] else []
        self.log_rules()

    def request(self, flow):
        if next(filter(lambda url: url in flow.request.pretty_url, self.rules), None):
            flow.response = http.HTTPResponse.make(404, b"How about studying", {"Content-Type": "text/html"})

    def log_rules(self):
        ctx.log.info("Blocked URLs are: %s" % str(self.rules))


addons = [
    Blocker()
]
