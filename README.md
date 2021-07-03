#### Mitm online
A simple add-on for mitm proxy to block certain URLs. This add-on stores the browsed urls in sqlite db along with the username and access timestamp.
It reads the blocked URL from DB periodically as well.

#### Launch
Example launch from FISH shell<br/>
 env sync_interval=1 env mode=prod env db_name="/home/fgandhi/Downloads/mitm/testdb/db.db" ./mitmdump -s ~/code/mitm-online/blocker.py

#### Run unittest
env mode=test venv/bin/python3.6 -m unittest blocker.py
