# Spraydar


Getting started:

1. install python 3
2. checkout spraydar repo
3. create a new virtual environment
4. pip install -r requirements.txt
5. python src/webpage.py to start the local Flask server. (defaults to http://127.0.0.1:5000/ )

Using the app:
1. Add the user_id of the mtnproject user you want to track using the 'add user ids' page. User ID is the 9 digit ID found in the URL: https://www.mountainproject.com/user/112446503/jack-lange. I.E.: "112446503"

Testing changes:
There is a 'main' block in tick_utils.py that is useful for testing changes to those functions.
