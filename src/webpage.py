from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta
from tick_utils import user_ticks_to_array, user_id_to_user_name, knit_ticks_by_date
import pprint


app = Flask(__name__)
app.secret_key = "secret" #TODO use a real secret
app.permanent_session_lifetime = timedelta(minutes=5)

@app.route("/")
def home():
    ticks = {}
    sorted_ticks = []
    if 'user_ids' in session:
        for user_id in session['user_ids']:
            user_ticks = user_ticks_to_array(user_id)[:5] #only show 5 most recent ticks per user for development ease
            user_name = user_id_to_user_name(user_id)
            ticks[user_name] = user_ticks
        sorted_ticks = knit_ticks_by_date(ticks) #It would be great to cache the ticks instead of re-scraping mtnproj every time.

    return render_template("index.html", sorted_ticks=sorted_ticks)



@app.route("/add-user-id", methods=["POST", "GET"])
def add_user_id():
    if request.method == "POST":
        session.permanent = True
        user_id = request.form["usrid"]
        if 'user_ids' in session:
            session["user_ids"].append(user_id) #TODO prevent adding duplicate users
        else:
            session['user_ids'] = [user_id]
        return redirect(url_for("add_user_id")) 
    else:
        return render_template("adduserid.html")



if __name__ == "__main__":
	app.run(debug=True)