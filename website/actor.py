from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .model import Patient, Employee, Doctor, Nurse, PhoneNumber, Inpatient, IpDetail, Outpatient, OpDetail, TreatAttribute, ExamineDetail, Use, UseFor, Medication, Effects
from . import db
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased


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
    input_id = request.args.get('input_id')

    # Aliases for inpatient-related tables
    inpatient_alias = aliased(Inpatient)
    ip_detail_alias = aliased(IpDetail)
    treat_attribute_alias = aliased(TreatAttribute)

    # Query for inpatient details including patient information
    inpatient_query = db.session.query(Patient, IpDetail, TreatAttribute)\
                    .join(inpatient_alias, Patient.inpatients)\
                    .join(ip_detail_alias, inpatient_alias.ip_details)\
                    .join(treat_attribute_alias, and_(
                        ip_detail_alias.ICode == treat_attribute_alias.ICode, 
                        ip_detail_alias.IP_visit == treat_attribute_alias.IP_visit))\
                    .filter(Patient.Code == input_id)

    # Aliases for outpatient-related tables
    outpatient_alias = aliased(Outpatient)
    op_detail_alias = aliased(OpDetail)
    examine_detail_alias = aliased(ExamineDetail)

    # Query for outpatient details including patient information
    outpatient_query = db.session.query(Patient, OpDetail, ExamineDetail)\
                    .join(outpatient_alias, Patient.outpatients)\
                    .join(op_detail_alias, outpatient_alias.op_details)\
                    .join(examine_detail_alias, and_(
                        op_detail_alias.OCode == examine_detail_alias.OCode, 
                        op_detail_alias.OP_visit == examine_detail_alias.OP_visit))\
                    .filter(Patient.Code == input_id)

    # Execute the queries
    inpatient_details = inpatient_query.all()
    outpatient_details = outpatient_query.all()

    patient_list = []

    # Add Inpatient details if available
    for patient, ip_detail, treat_attr in inpatient_details:
        patient_list.append({
            "id": patient.Code,
            "first_name": patient.First_Name,
            "last_name": patient.Last_Name,
            "phone_number": patient.Phone_number,
            "address": patient.Address,
            "date_of_birth": patient.Date_of_Birth,
            "gender": patient.Gender,
            "treatment_type": "Inpatient",
            "treatment_detail": {
                "IP_visit": ip_detail.IP_visit,
                "Diagnosis": ip_detail.Diagnosis,
                "Treatment": {
                    "DoctorID": treat_attr.DoctorID,
                    "Start_datetime": treat_attr.Start_datetime,
                    "End_datetime": treat_attr.End_datetime,
                    "Result": treat_attr.Result
                }
            }
        })

    # Add Outpatient details if available
    for patient, op_detail, examine_detail in outpatient_details:
        patient_list.append({
            "id": patient.Code,
            "first_name": patient.First_Name,
            "last_name": patient.Last_Name,
            "phone_number": patient.Phone_number,
            "address": patient.Address,
            "date_of_birth": patient.Date_of_Birth,
            "gender": patient.Gender,
            "treatment_type": "Outpatient",
            "treatment_detail": {
                "OP_visit": op_detail.OP_visit,
                "Examination": {
                    "DoctorID": examine_detail.DoctorID,
                    "Exam_datetime": examine_detail.Exam_datetime,
                    "Diagnosis": examine_detail.Diagnosis,
                    "Next_datetime": examine_detail.Next_datetime,
                    "Fee": examine_detail.Fee
                }
            }
        })

    print("Number of elements in patient_list:", len(patient_list))
    print("Treatment type of the first element in patient_list:", patient_list[0]['treatment_type'])

    return jsonify(patient_list)



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