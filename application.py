from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta
import pprint

from tick_utils import fetch_user, fetch_user_async, get_user_name, knit_ticks_by_date


app = Flask(__name__)
app.secret_key = "secret" #TODO use a real secret
app.permanent_session_lifetime = timedelta(minutes=5)

@app.route("/")
def home():
    ticks = {}
    sorted_ticks = []
    if 'user_ids' in session:
        watched_users = session['user_ids']
        for user_id in watched_users:
            fetch_user(user_id)
        sorted_ticks = knit_ticks_by_date(watched_users) #It would be great to cache the ticks instead of re-scraping mtnproj every time.

    return render_template("index.html", sorted_ticks=sorted_ticks)

@app.route("/manage-users", methods=["POST", "GET"])
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
        if action == "remove":
            print("removing ", user_id)
            session['user_ids'].remove(user_id)
        return redirect(url_for("manage_users")) 
    else:
        return render_template("manage.html", users=watched_users)



if __name__ == "__main__":
	app.run(debug=True, port=5001, threaded=True)