from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .model import Patient, Employee, Doctor, Nurse, PhoneNumber, Inpatient, IpDetail, Outpatient, OpDetail, TreatAttribute, ExamineDetail, Use, UseFor
from . import db
from sqlalchemy import func


actor = Blueprint('actor', __name__)

@login_required
@actor.route('/patient')
def patient():
    return render_template('patient.html')

@login_required
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
    last_patient = Patient.query.order_by(Patient.Code.desc()).first()
    if last_patient:
        next_code = str(int(last_patient.Code) + 1).zfill(9)  # Assuming ID is a numeric string
    else:
        next_code = '000000001'
 
    # Create new Patient object
    new_patient = Patient(
        Code = next_code,
        Password = password,
        Last_Name =last_name,
        First_Name =first_name,
        Phone_number =phone_number,
        Address =address,
        Date_of_Birth=date_of_birth,
        Gender=gender
    )


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

@actor.route('/search_by_doctor', methods=['GET'])
def search_by_doctor():
    doctor_name = request.args.get('doctor_name')
    doctor_id = request.args.get('doctor_id')

    # Query to find the doctor by name or ID
    if doctor_name:
        doctor = Doctor.query.join(Employee).filter(
            func.concat(Employee.First_Name, ' ', Employee.Last_Name) == doctor_name
        ).first()
    elif doctor_id:
        doctor = Doctor.query.filter_by(DoctorID=doctor_id).first()
    else:
        return jsonify({"error": "No search criteria provided"}), 400

    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404
    

    # Assuming you have a relationship set up in the Doctor model for TreatAttribute and ExamineDetail
    treat_attributes = TreatAttribute.query.filter_by(DoctorID=doctor.DoctorID).all()
    examine_details = ExamineDetail.query.filter_by(DoctorID=doctor.DoctorID).all()

    # Assuming you have relationships set up to access the patient from TreatAttribute and ExamineDetail
    patient_ids = {ta.ICode for ta in treat_attributes} | {ed.OCode for ed in examine_details}
    
    # Assuming Patient model has a Code attribute that corresponds to ICode/OCode
    patients = Patient.query.filter(Patient.Code.in_(patient_ids)).all()

    patient_list = [{
        "id": patient.Code,
        "first_name": patient.First_Name,
        "last_name": patient.Last_Name,
        "phone_number": patient.Phone_number,
        "address": patient.Address,
        "date_of_birth": patient.Date_of_Birth.strftime("%Y-%m-%d"),
        "gender": patient.Gender
    } for patient in patients]

    return jsonify(patient_list)


@actor.route('/doctor')
def doctor():
    return render_template("doctor.html")

@actor.route('/nurse')
def nurse():
    return render_template("nurse.html")