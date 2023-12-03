from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin

class Patient(db.Model, UserMixin):
    __tablename__ = 'patient'
    code = db.Column(db.CHAR(9), primary_key=True)
    OPCode = db.Column(db.CHAR(11), unique=True, nullable=True)
    IPCode = db.Column(db.CHAR(11), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(10), unique=True, nullable=False)
    address = db.Column(db.String(60), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.CHAR(1), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    def get_id(self):
        return self.code
    

def add_patient():
    if request.method == 'POST':
        # Get form data
        last_name = request.form.get('lastName')
        first_name = request.form.get('firstName')
        phone_number = request.form.get('phoneNumber')
        address = request.form.get('address')
        date_of_birth = request.form.get('dateOfBirth')
        gender = request.form.get('gender')
        doctor_assigned = request.form.get('doctorAssigned')
        medicine = request.form.get('medicine')

        # Create a new patient instance
        new_patient = Patient(
            Last_Name=last_name,
            First_Name=first_name,
            Phone_Number=phone_number,
            Address=address,
            Date_of_Birth=date_of_birth,
            Gender=gender,
            Doctor_Assigned=doctor_assigned,
            Medicine=medicine
        )

        # Add the patient to the database
        db.session.add(new_patient)
        db.session.commit()

        return "Patient added successfully"
