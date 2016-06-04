""" Command Line Interface Module """
import optparse
import sys
import os
import json
import hashlib
from functools import wraps
from flask import Flask, Response, request
from pymongo import MongoClient


app = Flask(__name__)
app.secret_key = os.urandom(24)

dbclient = MongoClient('localhost', 27017)
db = dbclient.outbit


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    valid_auth = False
    m = hashlib.md5()
    m.update(password)
    password_md5 = m.hexdigest()

    post = db.users.posts.find_one({"username": username})

    if post["password_md5"] == password_md5:
        valid_auth = True

    return valid_auth

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route("/", methods=["POST"])
@requires_auth
def outbit_base():
    indata = request.get_json()
    dat = None
    status = 200

    if indata["category"] == "/" and indata["action"] == "ping":
        dat = json.dumps({"response": "pong"})
    elif indata["category"] == "/users" and indata["action"] == "add":
        (username, password) = indata["options"].split(",")

        m = hashlib.md5()
        m.update(password)
        password_md5 = str(m.hexdigest())

        post = {"username": username, "password_md5": password_md5}
        db.users.posts.insert_one(post)

        print("Creating User %s" % username)

        dat = json.dumps({"response": "success created %s" % username})
    else:
        status=403

    resp = Response(response=dat, status=status, mimetype="application/json")
    return(resp)


class Cli(object):
    """ outbit CLI """

    def __init__(self):
        """ Setup Arguments and Options for CLI """
        # Parse CLI Arguments
        parser = optparse.OptionParser()
        parser.add_option("-s", "--server", dest="server",
                          help="IP address or hostname of outbit-api server",
                          metavar="SERVER",
                          default="127.0.0.1")
        parser.add_option("-p", "--port", dest="port",
                          help="tcp port of outbit-api server",
                          metavar="PORT",
                          default="8088")
        parser.add_option("-t", "--secure", dest="is_secure",
                          help="Use SSL",
                          metavar="SECURE",
                          action="store_true")
        parser.add_option("-d", "--debug", dest="is_debug",
                          help="Debug Mode",
                          metavar="DEBUG",
                          action="store_true")
        (options, args) = parser.parse_args()
        self.server = options.server
        self.port = int(options.port)
        self.is_secure = options.is_secure
        self.is_debug = options.is_debug

    def run(self):
        """ EntryPoint Of Application """

        # First Time Defaults, Setup superadmin if it doesnt exist
        default_user = "superadmin"
        default_password = "superadmin"
        post = db.users.posts.find_one({"username": default_user})
        if post is None:
            m = hashlib.md5()
            m.update(default_password)
            default_password_md5 = str(m.hexdigest())

            post = {"username": default_user, "password_md5": default_password_md5}
            db.users.posts.insert_one(post)

        # Start API Server
        print("Starting outbit api server on %s://%s:%d" % ("https" if
            self.is_secure else "http", self.server, self.port))
        if self.is_secure:
            print("Does not support SSL yet")
            sys.exit(1)
        else:
            app.run(host=self.server, port=self.port, debug=self.is_debug)



