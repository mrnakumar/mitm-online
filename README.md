#### Mitm online
A simple add-on for mitm proxy to block certain URLs. This add-on stores the browsed urls in sqlite db along with the username and access timestamp.
It reads the blocked URL from DB periodically as well.

#### Launch Proxy
Example launch from FISH shell<br/>
 1. Setup python virtual environment with python 3.9 or later.</br> 
 2. Install mitmproxy.</br>
 3. Clone this repository. Assuming this repoisotory is cloned in `~/code/mitm-online`<br/>
 4. Launch by using the following command<br/>
      `env sync_interval=1 env mode=prod env db_name="/home/fgandhi/Downloads/mitm/testdb/db.db" ./mitmdump -s ~/code/mitm-online/blocker.py`</br>
    In the above command the `./mitmdump` is the mitmdump command from mitmproxy. If the mitmdump is in system path then `mitmdubmp` can be used instead of a relative path.</br>
    The sync_interval is the duration in minutes after which the browsed URLs are inserted into DB. This is to reduce the load on DB by avoiding frequent writes.</br>
    The mode should be 'prod' when wanting to launch the proxy. For running python tests, please see section "Run unittest" below.</br>

#### Run unittest
env mode=test venv/bin/python3.6 -m unittest blocker.py

#### Launch Admin Web UI
To block/unblock certain hostnames, the admin UI should be used.

##### Launch Admin Web UI in development mode
 1. Export the path to the application's controller python file by using the following command:</br>
     `export FLASK_APP=~/code/mitm-online/admin_controller.py`

 2. Run the app by using the following command:</br>
     `flask run`
