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

    inpatients = db.relationship('Inpatient', backref='patient', lazy=True)
    outpatients = db.relationship('Outpatient', backref='patient', lazy=True)

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

class Inpatient(db.Model):
    __tablename__ = 'inpatient'
    ICode = db.Column(db.CHAR(9), db.ForeignKey('patient.Code'), primary_key=True)
    # Assuming you have a relationship with Patient model
    ip_details = db.relationship('IpDetail', backref='inpatient', lazy=True)


class IpDetail(db.Model):
    __tablename__ = 'ip_detail'
    ICode = db.Column(db.CHAR(9), db.ForeignKey('inpatient.ICode'), primary_key=True)
    IP_visit = db.Column(db.Integer, primary_key=True)
    Admission_date = db.Column(db.Date, nullable=False)
    Diagnosis = db.Column(db.VARCHAR(255), nullable=False)
    Sickroom = db.Column(db.Integer, nullable=False)
    Discharge_date = db.Column(db.Date, nullable=False)
    Fee = db.Column(db.Integer, nullable=False)
    Nurse_ID = db.Column(db.CHAR(9), db.ForeignKey('nurse.NurseID'), nullable=False)

class TreatAttribute(db.Model):
    __tablename__ = 'treat_attribute'
    ICode = db.Column(db.CHAR(9), db.ForeignKey('ip_detail.ICode'), primary_key=True)
    IP_visit = db.Column(db.Integer, db.ForeignKey('ip_detail.IP_visit'), primary_key=True)
    DoctorID = db.Column(db.CHAR(9), db.ForeignKey('doctor.DoctorID'), primary_key=True)
    Start_datetime = db.Column(db.DateTime, primary_key=True)
    End_datetime = db.Column(db.DateTime, primary_key=True)
    Result = db.Column(db.VARCHAR(255), nullable=False)


class Outpatient(db.Model):
    __tablename__ = 'outpatient'
    OCode = db.Column(db.CHAR(9), db.ForeignKey('patient.Code'), primary_key=True)
    # Assuming you have a relationship with Patient model
    op_details = db.relationship('OpDetail', backref='inpatient', lazy=True)


class OpDetail(db.Model):
    __tablename__ = 'op_detail'
    OCode = db.Column(db.CHAR(9), db.ForeignKey('outpatient.OCode'), primary_key=True)
    OP_visit = db.Column(db.Integer, primary_key=True)



class ExamineDetail(db.Model):
    __tablename__ = 'examine_detail'
    OCode = db.Column(db.CHAR(9), db.ForeignKey('op_detail.OCode'), primary_key=True)
    OP_visit = db.Column(db.Integer, db.ForeignKey('op_detail.OP_visit'), primary_key=True)
    DoctorID = db.Column(db.CHAR(9), db.ForeignKey('doctor.DoctorID'), primary_key=True)
    Exam_datetime = db.Column(db.DateTime, primary_key=True)
    Diagnosis = db.Column(db.VARCHAR(255), nullable=False)
    Next_datetime = db.Column(db.DateTime, nullable=True)
    Fee = db.Column(db.Integer, nullable=False)


class Use(db.Model):
    __tablename__ = 'use'
    MCode = db.Column(db.CHAR(9), db.ForeignKey('medication.Code'), primary_key=True)
    ICode = db.Column(db.CHAR(9), primary_key=True)
    IP_visit = db.Column(db.Integer, primary_key=True)
    DoctorID = db.Column(db.CHAR(9), primary_key=True)
    Start_datetime = db.Column(db.DateTime, primary_key=True)
    End_datetime = db.Column(db.DateTime, primary_key=True)
    NumOfMed = db.Column(db.Integer, nullable=False)


class UseFor(db.Model):
    __tablename__ = 'use_for'
    MCode = db.Column(db.CHAR(9), db.ForeignKey('medication.Code'), primary_key=True)
    OCode = db.Column(db.CHAR(9), primary_key=True)
    OP_visit = db.Column(db.Integer, primary_key=True)
    DoctorID = db.Column(db.CHAR(9), primary_key=True)
    Exam_datetime = db.Column(db.DateTime, primary_key=True)
    NumOfMed = db.Column(db.Integer, nullable=False)

class Medication(db.Model):
    __tablename__ = 'medication'
    Code = db.Column(db.CHAR(9), primary_key=True)
    Name = db.Column(db.String(45), nullable=False)
    Price = db.Column(db.Integer, nullable=False)
    Expired_Date = db.Column(db.Date, nullable=False)

    # Relationship with Effects
    effects = db.relationship('Effects', backref='medication', lazy=True)


class Effects(db.Model):
    __tablename__ = 'effects'
    Code = db.Column(db.CHAR(9), db.ForeignKey('medication.Code'), primary_key=True)
    Effects = db.Column(db.String(45), primary_key=True)