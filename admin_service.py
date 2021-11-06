from itertools import groupby
from flask import render_template
from datetime import datetime


class DatabaseService:
    def get_browsed(self, db):
        browsed = map(lambda row: Browsed(*row), self.get_browsed_hostnames(db))
        blocked = db.read_blocked()
        ignored = db.read_ignored()
        not_blocked_not_ignored = map(
            timestamp_to_datetime,
            filter(
                lambda e: (e.host not in blocked) and (e.host not in ignored), browsed
            ),
        )
        result = []
        for key, group in groupby(
            sorted(not_blocked_not_ignored, key=lambda e: e.host), lambda e: e.host
        ):
            result.append(
                BrowsedByHost(
                    key, sorted(list(group), key=lambda e: e.accessed_on, reverse=True)
                )
            )
        return render_template("browsed.html", browsed=result)

    def get_blocked(self, db):
        blocked = db.read_blocked()
        result = sorted(blocked)
        return render_template("blocked.html", blocked=result)

    def get_ignored(self, db):
        ignored = db.read_ignored()
        result = sorted(ignored)
        return render_template("ignored.html", ignored=result)

    def block_hostname(self, db, hostname):
        db.write_blocked(
            [
                hostname,
            ]
        )
        self.unignore_hostname(db, hostname)

    def unblock_hostname(self, db, hostname):
        db.unblock(
            [
                hostname,
            ]
        )

    def ignore_hostname(self, db, hostname):
        db.write_ignored(
            [
                hostname,
            ]
        )
        self.unblock_hostname(db, hostname)

    def unignore_hostname(self, db, hostname):
        db.unignore(
            [
                hostname,
            ]
        )

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


def timestamp_to_datetime(browsed):
    accessed_on = datetime.utcfromtimestamp(browsed.accessed_on).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    return Browsed(browsed.user, browsed.host, browsed.url, accessed_on)
