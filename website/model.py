from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin

class Patient(db.Model, UserMixin):
    __tablename__ = 'patient'
    Code = db.Column(db.CHAR(9), primary_key=True)
    OPCode = db.Column(db.CHAR(11), unique=True, nullable=True)
    IPCode = db.Column(db.CHAR(11), unique=True, nullable=True)
    Password = db.Column(db.String(16), nullable=False)
    Phone_number = db.Column(db.String(10), unique=True, nullable=False)
    Address = db.Column(db.String(60), nullable=False)
    Date_of_Birth = db.Column(db.Date, nullable=False)
    Gender = db.Column(db.CHAR(1), nullable=False)
    First_Name = db.Column(db.String(30), nullable=False)
    Last_Name = db.Column(db.String(30), nullable=False)

    def get_id(self):
        return self.Code
    
class Employee(db.Model, UserMixin):
    __tablename__ = 'employee'
    EmployeeID = db.Column(db.CHAR(9), primary_key=True)
    Password = db.Column(db.String(16), nullable=False)
    DCode = db.Column(db.Integer, unique=True, nullable=True)   
    DegreeYear = db.Column(db.Integer, nullable=True)
    DegreeName = db.Column(db.CHAR(45), nullable=True)
    First_Name = db.Column(db.String(30), nullable=False)
    Last_Name = db.Column(db.String(30), nullable=False)
    Gender = db.Column(db.CHAR(1), nullable=False)
    Date_of_Birth = db.Column(db.Date, nullable=False)
    Address = db.Column(db.String(60), nullable=False)
    Start_date= db.Column(db.Date, nullable=False)
    
    def get_id(self):
        return self.EmployeeID
    
class PhoneNumber(db.Model, UserMixin):
    __tablename__ = 'phonenumber'
    EmployeeID = db.Column(db.CHAR(9), db.ForeignKey('employee.EmployeeID'), primary_key=True)
    Phone_no = db.Column(db.String(10), primary_key=True)

class Doctor(db.Model, UserMixin):
    __tablename__ = 'doctor'
    DoctorID = db.Column(db.CHAR(9), db.ForeignKey('employee.EmployeeID'), primary_key=True)
    employee = db.relationship('Employee', backref='doctor', lazy=True)

class Nurse(db.Model):
    __tablename__ = 'nurse'
    NurseID = db.Column(db.CHAR(9), db.ForeignKey('employee.EmployeeID'), primary_key=True)
    employee = db.relationship('Employee', backref='nurse', lazy=True)
