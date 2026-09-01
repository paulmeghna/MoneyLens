from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    type = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.Date, nullable=False)    

class Budget(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    month = db.Column(db.Integer, nullable=False)

    year = db.Column(db.Integer, nullable=False)

    category = db.Column(db.String(50), nullable=False)

    amount = db.Column(db.Float, nullable=False)

    # A user can have only one budget for
    # a specific category in a specific month and year.
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "month",
            "year",
            "category",
            name="unique_user_budget"
        ),
    )



