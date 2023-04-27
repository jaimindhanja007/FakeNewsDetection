import pyrebase
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    abort,
    url_for,
)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
import pyrebase
from Scraper.Scraper import *


tfvect = TfidfVectorizer(stop_words="english", max_df=0.7)
loaded_model = pickle.load(open("model.pkl", "rb"))
dataframe = pd.read_csv("news.csv")
x = dataframe["text"]
y = dataframe["label"]
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)


def fake_news_det(news):
    tfid_x_train = tfvect.fit_transform(x_train)
    tfid_x_test = tfvect.transform(x_test)
    input_data = [news]
    vectorized_input_data = tfvect.transform(input_data)
    prediction = loaded_model.predict(vectorized_input_data)
    return prediction


app = Flask(__name__)  # Initialze flask constructor

# Add your own details
config = {
    "apiKey": "AIzaSyDBYVCt74OEEt5nS_Tcf_2iHzm4gXaMRKs",
    "authDomain": "fakenews-6c069.firebaseapp.com",
    "databaseURL": "https://fakenews-6c069-default-rtdb.firebaseio.com",
    "projectId": "fakenews-6c069",
    "storageBucket": "fakenews-6c069.appspot.com",
    "messagingSenderId": "285735704642",
    "appId": "1:285735704642:web:948dac0293ee50e12935db",
    "measurementId": "G-JREKP78MM9",
    "databaseURL": "",
}

# initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

# Initialze person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}


# Home
@app.route("/")
def home():
    return render_template("home_page.html")


@app.route("/home")
def home_():
    return render_template("home_page.html")


# Login
@app.route("/login")
def login():
    return render_template("login.html")


# Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/contact_us")
def contact():
    return render_template("contact_us.html")

@app.route("/about_us")
def about():
    return render_template("about_us.html")

# Welcome page
@app.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
        return render_template(
            "welcome.html", email=person["email"], name=person["name"]
        )
    else:
        return redirect(url_for("login"))


# News detection page
@app.route("/news_detection")
def news_detection():
    if person["is_logged_in"] == True:
        return render_template("news_detection.html")
    else:
        return redirect(url_for("login"))


@app.route("/result", methods=["POST"])
def result():
    inputm = request.form["input-method"]
    inputd = request.form["input-data"]
    try:
        newsl = request.form["select-newsletter"]
        if newsl == "TimesofIndia":
            data = timesOfIndiaScraper(inputd)
        elif newsl == "TheHindu":
            data = theHinduscraper(inputd)
        elif newsl == "TheGuardian":
            data = theguardianscraper(inputd)
        else:
            return render_template("result.html", result=fake_news_det(inputd))
        return render_template("result.html", result=fake_news_det(data))
    except:
        newsl = 0
        return render_template("result.html", result=fake_news_det(inputd))


# If someone clicks on login, they are redirected to /result
@app.route("/resultlogin", methods=["POST", "GET"])
def resultlogin():
    unsuccessful = "Please check your credentials"
    successsful = "Login successful"
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["pass"]
        try:
            auth.sign_in_with_email_and_password(email, password)
            global person
            person["is_logged_in"] = True
            # return render_template("news_detection.html", s=successsful)
            return redirect(url_for("news_detection"))

        except:
            return render_template("login.html", us=unsuccessful)
    return render_template("login.html")


# If someone clicks on register, they are redirected to /register
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":  # Only listen to POST
        result = request.form  # Get the data submitted
        email = result["email"]
        password = result["pass"]
        confirmpass = result["confirmpass"]
        name = result["name"]
        try:
            if password != confirmpass:
                # If passwords do not match
                return render_template("signup.html", us="Passwords do not match")
            # Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            # Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            # Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            # Append data to the firebase realtime database
            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)
            # Go to welcome page
            return redirect(url_for("welcome"))
        except:
            # If there is any error, redirect to register
            return redirect(url_for("register"))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for("news_detection"))
        else:
            return redirect(url_for("register"))


if __name__ == "__main__":
    app.run(port=2000, debug=True)