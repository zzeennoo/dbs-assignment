from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .model import Patient, Employee, Doctor, Nurse, PhoneNumber, Inpatient, IpDetail, Outpatient, OpDetail, TreatAttribute, ExamineDetail, Use, UseFor, Medication, Effects
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

    print('f')

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
    
    treat_attributes = TreatAttribute.query.filter_by(DoctorID=doctor.DoctorID).all()
    examine_details = ExamineDetail.query.filter_by(DoctorID=doctor.DoctorID).all()

    patient_ids = {ta.ICode for ta in treat_attributes} | {ed.OCode for ed in examine_details}
    
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

@actor.route('/search_by_patient', methods=['GET'])
def search_by_patient():
    patient_name = request.args.get('patient_name')
    phone_number = request.args.get('phone_number')
    print('f')
    # Query to find the doctor by name or ID
    if patient_name:
        patients = Patient.query.filter(func.concat(Patient.First_Name, ' ', Patient.Last_Name) == patient_name).first()
    elif phone_number:
        patients = Patient.query.filter_by(PhoneNumber = phone_number).first()
    else:
        return jsonify({"error": "No search criteria provided"}), 400

    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

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

@actor.route('/export_patient_details', methods=['GET'])
def export_patient_details():
    patient_id = request.args.get('patient_id')

    ip_code = 'IP'+patient_id
    op_code = 'OP'+patient_id
    
    # Assuming you have methods to get the patient details
    inpatient_details = get_inpatient_details(ip_code)
    outpatient_details = get_outpatient_details(op_code)
    
    # Combine the details into one dictionary
    patient_details = {
        'inpatient': inpatient_details,
        'outpatient': outpatient_details
    }

    return jsonify(patient_details)

def get_inpatient_details(ip_code):
    inpatient = Inpatient.query.filter_by(ICode=ip_code).first()

    if not inpatient:
        return None  # or return an empty dictionary if preferred

    # Fetch the details of the inpatient stay
    ip_details_list = []
    for ip_detail in inpatient.ip_details:
        # For each inpatient stay, fetch the treatment attributes
        treat_attributes_list = []
        for treat_attribute in ip_detail.treat_attribute:
            treat_attributes_list.append({
                "doctor_id": treat_attribute.DoctorID,
                "start_datetime": treat_attribute.Start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "end_datetime": treat_attribute.End_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "result": treat_attribute.Result
            })
        
        # Add the detail of each stay to the list
        ip_details_list.append({
            "ip_visit": ip_detail.IP_visit,
            "admission_date": ip_detail.Admission_date.strftime("%Y-%m-%d"),
            "diagnosis": ip_detail.Diagnosis,
            "sickroom": ip_detail.Sickroom,
            "discharge_date": ip_detail.Discharge_date.strftime("%Y-%m-%d"),
            "fee": ip_detail.Fee,
            "nurse_id": ip_detail.Nurse_ID,
            "treat_attributes": treat_attributes_list
        })

    return ip_details_list

def get_outpatient_details(op_code):
    # Fetch the outpatient record that corresponds to the given OP code
    outpatient = Outpatient.query.filter_by(OCode=op_code).first()

    if not outpatient:
        return None  # or return an empty dictionary if preferred

    # Fetch the details of the outpatient visits
    op_details_list = []
    for op_detail in outpatient.op_details:
        # For each outpatient visit, fetch the examination details
        examine_details_list = []
        for examine_detail in op_detail.examine_details:
            examine_details_list.append({
                "doctor_id": examine_detail.DoctorID,
                "exam_datetime": examine_detail.Exam_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "diagnosis": examine_detail.Diagnosis,
                "next_datetime": examine_detail.Next_datetime.strftime("%Y-%m-%d %H:%M:%S") if examine_detail.Next_datetime else None,
                "fee": examine_detail.Fee
            })
        
        # Add the detail of each outpatient visit to the list
        op_details_list.append({
            "op_visit": op_detail.OP_visit,
            "examine_details": examine_details_list
        })

    return op_details_list


@actor.route('/doctor')
def doctor():
    return render_template("doctor.html")

@actor.route('/nurse')
def nurse():
    return render_template("nurse.html")