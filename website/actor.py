from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .model import Patient
from . import db

actor = Blueprint('actor', __name__)

@login_required
@actor.route('/patient')
def patient():
    return render_template('patient.html')



@actor.route('/admin')
def admin():
    # Query all patients from the database
    patients = Patient.query.all()
    return render_template('admin.html', patients=patients)

@actor.route('/add_patient', methods=['POST'])
def add_patient():
    # Get data from form submission
    last_name = request.form.get('lastName')
    first_name = request.form.get('firstName')
    phone_number = request.form.get('phoneNumber')
    address = request.form.get('address')
    date_of_birth = request.form.get('dateOfBirth')
    gender = request.form.get('gender')
    password = request.form.get('password')

    #Generate new Code(ID) for patient
    last_patient = Patient.query.order_by(Patient.code.desc()).first()
    if last_patient:
        next_code = str(int(last_patient.code) + 1).zfill(9)  # Assuming ID is a numeric string
    else:
        next_code = '000000001'

    
    # Create new Patient object
    new_patient = Patient(
        code = next_code,
        password = password,
        last_name=last_name,
        first_name=first_name,
        phone_number=phone_number,
        address=address,
        date_of_birth=date_of_birth,
        gender=gender,
        OPCode="OP" + next_code,  
        IPCode="IP" + next_code  
    )


    # Print new patient data
    print("New Patient Data:")
    print(f"Code: {new_patient.code}")
    print(f"OPCode: {new_patient.OPCode}")
    print(f"IPCode: {new_patient.IPCode}")
    print(f"Password: {new_patient.password}")  # Be cautious with printing passwords
    print(f"Phone Number: {new_patient.phone_number}")
    print(f"Address: {new_patient.address}")
    print(f"Date of Birth: {new_patient.date_of_birth}")
    print(f"Gender: {new_patient.gender}")
    print(f"First Name: {new_patient.first_name}")
    print(f"Last Name: {new_patient.last_name}")

    # Add to the database session and commit
    db.session.add(new_patient)

    try:
        db.session.commit()
        flash('New patient added successfully!', 'success')
        print("success")
    except Exception as e:
        db.session.rollback()
        flash('Error adding patient: ' + str(e), 'danger')
        print("fail")

    # Redirect back to the admin page
    return redirect(url_for('actor.admin'))





@actor.route('/doctor_and_nurse')
def doctor_and_nurse():
    return render_template('doctor_and_nurse.html')