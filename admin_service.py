from flask import render_template

class DatabaseService:
    def render_admin_page(self, db):
        browsed = self.get_browsed_hostnames(db)
        blocked = db.read_blocked()
        not_blocked  = filter(lambda hostname: hostname not in blocked, browsed)
        return render_template('admin.html', hostnames = not_blocked)

    def block_hostname(self, db, hostname):
        db.write_blocked([hostname,])

    def get_browsed_hostnames(self, db):
        hostnames = db.read_browsed()
        hostnames_sorted = sorted(hostnames)
        return hostnames_sorted

