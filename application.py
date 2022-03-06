from flask import Flask, redirect, url_for, render_template, request, session, make_response
from datetime import timedelta
import pprint
import os

from tick_utils import fetch_user, fetch_user_async, get_user_name, knit_ticks_by_date
from db_utils import load_followed_users, follow_user

application = Flask(__name__)
application.secret_key = "secret" #TODO use a real secret
application.permanent_session_lifetime = timedelta(minutes=5)

#configs for auth to the dynamo db
if  os.environ.get('env') != 'live':
    os.environ['AWS_CONFIG_FILE'] = '~/.aws/config' #ask me for the config file so you can run locally
    os.environ['AWS_PROFILE'] = "spraydar-app"
# os.environ['AWS_ACCESS_KEY_ID'] = 
# os.environ['AWS_SECRET_ACCESS_KEY'] = 
os.environ['AWS_DEFAULT_REGION'] = "us-west-2"

@application.route("/")
def home():
    ticks = {}
    sorted_ticks = []
    active_user = request.cookies.get("activeUserID", None)
    if active_user  and 'user_ids' not in session.keys():
        session['user_ids'] = load_followed_users(active_user)
    
    if 'user_ids' in session:
        watched_users = session['user_ids']
        for user_id in watched_users:
            fetch_user(user_id)
        if watched_users != []:
            sorted_ticks = knit_ticks_by_date(watched_users) #It would be great to cache the ticks instead of re-scraping mtnproj every time.

    return render_template("index.html", sorted_ticks=sorted_ticks, active_user=active_user)

@application.route("/manage-users", methods=["POST", "GET"])
def manage_users():
    user_ids = session.get('user_ids', [])
    watched_users = {user_id: get_user_name(user_id) for user_id in user_ids}

    if request.method == "POST":
        session.permanent = True
        user_id = request.form["usrid"]
        action = request.form["action"]
        if action == "add":
            if user_id not in user_ids:
                if 'user_ids' in session:
                    session["user_ids"].append(user_id)
                    
                else:
                    session['user_ids'] = [user_id]
            fetch_user_async(user_id)
            active_user = request.cookies.get("activeUserID", None)
            if active_user:
                follow_user(active_user, user_id)
        if action == "remove":
            print("removing ", user_id)
            session['user_ids'].remove(user_id)
        return redirect(url_for("manage_users")) 
    else:
        return render_template("manage.html", users=watched_users)


@application.route("/active", methods=["POST", "GET"])
def active():
    if request.method == "GET":
        return render_template("active.html")
    elif request.method == "POST":
        print("here?")
        user = request.form['usrid']

        resp = make_response(render_template("active.html"))
        resp.set_cookie('activeUserID', user)
        return resp



if __name__ == "__main__":
	application.run(debug=True, port=5001, threaded=True)