from flask import render_template

class DatabaseService:

    def render_admin_page(self, db):
        hostnames = self.get_browsed_hostnames(db)
        return render_template('admin.html', hostnames = hostnames)

    def block_hostname(self, db, hostname):
        db.write_blocked([hostname,])

    def get_browsed_hostnames(self, db):
        hostnames = db.read_browsed()
        hostnames_sorted = sorted(hostnames)
        return hostnames_sorted

