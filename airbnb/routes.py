# Matthew Lim
# Spring 2021
# ITP_499 TTH 12:30PM
# Final Project

from flask import redirect, render_template, request, session, url_for, send_file
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from airbnb import app, db


# Main endpoint, leads to landing page
@app.route("/")
def home():
    return render_template("main.html")


# POST request for submitting location, reroutes to get request for specified location
@app.route("/action/location", methods=["POST"])
def assign():
    # Reroute to home if location doesn't exist in csv
    param = (str(request.form["location"]).title(),)
    if len(db.engine.execute('''SELECT AVG('price') FROM listings WHERE neighbourhood = ?''', param).fetchall()) == 0:
        return redirect(url_for('home'))
    return redirect(url_for('location', loc=str(request.form["location"]).title(), amount=request.form["amount"]))


# Return info page for location
@app.route("/location/<loc>/<amount>", methods=["GET"])
def location(loc, amount):
    if not amount.isnumeric():
        return redirect(url_for('location', loc=loc, amount=1000))
    param = (loc,)
    # Manipulate dataframe and compute various data about location
    number = len(db.engine.execute("SELECT * FROM listings WHERE neighbourhood = ?", param).fetchall())
    price = db.engine.execute("SELECT AVG(price) FROM listings WHERE neighbourhood = ?", param).fetchone()[0]
    availability = int(db.engine.execute("SELECT AVG(availability_365) FROM listings WHERE neighbourhood = ?"
                                    , param).fetchone()[0])

    return render_template("info.html", location=loc, number=number, price="${:.2f}".format(price),
                           days="{:.2f}".format(availability), amount=amount)


# Visualize data using histogram of listings sorted by nightly price
@app.route("/visualize/<loc>/<above>", methods=["GET"])
def visualize(loc, above):
    fig, ax = plt.subplots(1, 1)
    room_types = [0, 1, 2, 3]
    for r in room_types:
        param = (r, float(above), loc,)
        data = db.engine.execute("SELECT price from listings WHERE room_type = ? AND price <= ? AND neighbourhood = ?",
                            param)
        prices = [item for tuple in data.fetchall() for item in tuple]
        print(prices)
        ax.hist(x=prices, bins=30, alpha=0.5, label=r)
    ax.set_xlabel("Price ($)")
    ax.set_ylabel("# of Properties")
    ax.title.set_text("(Existing) Airbnb Nightly Prices < $" + above)
    plt.grid()
    plt.tight_layout()
    plt.legend(['Existing home/apt', 'Hotel room', 'Private room', 'Shared room'])
    img_bytes = BytesIO()
    fig.savefig(img_bytes)
    img_bytes.seek(0)
    return send_file(img_bytes, mimetype='image/png')


# Reroute to prediction page, displaying listed price
@app.route("/prediction/<pred>", methods=['GET'])
def prediction(pred):
    return render_template("prediction.html", price=pred)


# POST request to submit prediction parameters for nightly price
@app.route("/action/predict", methods=["POST"])
def predict():
    # Modifies categorical data to be numerical for the regressor

    x = db.engine.execute(
        "SELECT latitude, longitude, room_type, minimum_nights, listing_count, availability_365 FROM listings").fetchall()
    y_unformatted = db.engine.execute("SELECT price FROM listings").fetchall()
    y = [item for tuple in y_unformatted for item in tuple]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.25, random_state=0)
    # Using RFR as it yieled the highest performance out of the ones tested
    rfr = RandomForestRegressor()
    rfr.fit(x_train, y_train)
    price = rfr.predict([[request.form['latitude'], request.form['longitude'], request.form['room_type'],
                          request.form['minimum_nights'], request.form['count'],
                          request.form['avail']]])
    return redirect(url_for('prediction', pred=price))


# Visualization endpoint for parameter weights/importance in predicting price
@app.route("/visualize_ml", methods=['GET'])
def visualize_ml():
    fig, ax = plt.subplots(1, 1)
    x = db.engine.execute(
        "SELECT latitude, longitude, room_type, minimum_nights, listing_count, availability_365 FROM listings").fetchall()
    y_unformatted = db.engine.execute("SELECT price FROM listings").fetchall()
    y = [item for tuple in y_unformatted for item in tuple]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.25, random_state=0)
    rfr = RandomForestRegressor()
    rfr.fit(x_train, y_train)
    headers = ["name", "score"]

    values = sorted(zip(['latitude', 'longitude', 'room_type', 'minimum_nights', 'listing_count', 'availability_365'],
                        rfr.feature_importances_), key=lambda x: x[1] * -1)
    feature_importance = pd.DataFrame(values, columns=headers)
    feature_importance = feature_importance.sort_values(by=['score'], ascending=False)
    features = feature_importance['name'][:15]
    y_pos = np.arange(len(features))
    scores = feature_importance['score'][:15]
    plt.bar(y_pos, scores, alpha=0.5)
    plt.ylabel('Score out of 1')
    plt.xlabel('Features')
    plt.title('Importance of Features')
    plt.xticks(np.arange(6),
               ['Latitude', 'Longitude', 'Room Type', 'Minimum Nights', 'Number of Host Listings', 'Availability/365'])
    plt.xticks(rotation=-45, rotation_mode='anchor')
    plt.tight_layout()
    img_bytes = BytesIO()
    plt.savefig(img_bytes)
    img_bytes.seek(0)

    return send_file(img_bytes, mimetype='image/png')


# Handles any exception/errors, reroutes back to home endpoint
@app.errorhandler(Exception)
def handle_error(error):
    message = [str(x) for x in error.args]
    status_code = 500
    success = False
    response = {
        'success': success,
        'error': {
            'type': error.__class__.__name__,
            'message': message
        }
    }
    print("Error:")
    print(message)
    return redirect(url_for('home'))
