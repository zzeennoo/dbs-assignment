from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin

class Patient(db.Model, UserMixin):
    __tablename__ = 'patient'
    Code = db.Column(db.CHAR(9), primary_key=True)
    OPCode = db.Column(db.CHAR(11), unique=True, nullable=True)
    IPCode = db.Column(db.CHAR(11), unique=True, nullable=True)
    Password = db.Column(db.String(255), nullable=False)
    Phone_number = db.Column(db.String(10), unique=True, nullable=False)
    Address = db.Column(db.String(60), nullable=False)
    Date_of_Birth = db.Column(db.Date, nullable=False)
    Gender = db.Column(db.CHAR(1), nullable=False)
    First_Name = db.Column(db.String(30), nullable=False)
    Last_Name = db.Column(db.String(30), nullable=False)

    def get_id(self):
        return self.Code
    

    