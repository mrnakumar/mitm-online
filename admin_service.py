from itertools import groupby
from flask import render_template

class DatabaseService:
    def render_admin_page(self, db):
        browsed = map(lambda row: Browsed(*row), self.get_browsed_hostnames(db))
        blocked = db.read_blocked()
        ignored = db.read_ignored()
        not_blocked_not_ignored  = filter(lambda e: (e.host not in blocked) and (e.host not in ignored), browsed)
        result = []
        for key , group in groupby(sorted(not_blocked_not_ignored, key = lambda e: e.host), lambda e: e.host):
            result.append(BrowsedByHost(key, sorted(list(group), key = lambda e: e.accessed_on, reverse=True)))
        return render_template('admin.html', browsed = result)

    def block_hostname(self, db, hostname):
        db.write_blocked([hostname,])

    def ignore_hostname(self, db, hostname):
        db.write_ignored([hostname,])

    def get_browsed_hostnames(self, db):
        rows = db.read_browsed()
        rows_sorted = sorted(rows)
        return rows_sorted

class Browsed:
    def __init__(self, user, url_host, full_url, accessed_on):
        self.user = user
        self.host = url_host
        self.url = full_url
        self.accessed_on = accessed_on

class BrowsedByHost:
    def __init__(self, host, group):
        self.host = host
        self.group = group
