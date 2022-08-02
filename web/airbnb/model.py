import pandas as pd
from airbnb import db
from flask_sqlalchemy import SQLAlchemy

class Listing(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    neighbourhood = db.Column(db.String(25))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    room_type = db.Column(db.Integer)
    price = db.Column(db.Integer)
    minimum_nights = db.Column(db.Integer)
    listing_count = db.Column(db.Integer)
    availability_365 = db.Column(db.Integer)

    @staticmethod
    def insert_all():
        df = pd.read_csv("listings.csv")
        df.replace(to_replace="Entire home/apt", value=0, inplace=True)
        df.replace(to_replace="Hotel room", value=1, inplace=True)
        df.replace(to_replace="Private room", value=2, inplace=True)
        df.replace(to_replace="Shared room", value=3, inplace=True)
        for row in df.itertuples():
            listing = Listing(neighbourhood=row.neighbourhood, latitude=row.latitude, longitude=row.longitude,
                              room_type=row.room_type, price=row.price, minimum_nights=row.minimum_nights,
                              listing_count=row.calculated_host_listings_count, availability_365=row.availability_365)
            db.session.add(listing)
            db.session.commit()
