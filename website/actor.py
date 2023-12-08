from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .model import Patient, Employee, Doctor, Nurse, PhoneNumber, Inpatient, IpDetail, Outpatient, OpDetail, TreatAttribute, ExamineDetail, Use, UseFor, Medication, Effects
from . import db
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased
from datetime import datetime

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

@actor.route('/add_examine')
def add_examine():
    patient_code = request.form.get('e_patient_code')
    op_visit = request.form.get('e_OP_visit')
    doctor_id = request.form.get('e_doctor_id')
    exam_date = request.form.get('e_exam_date')
    next_date = request.form.get('e_next_date')
    diagnosis = request.form.get('e_diagnosis')
    exam_fee = request.form.get('e_fee')
    #medicines = request.form.getlist('medicines') 

    #for outpatient table
    outpatient = Outpatient.query.filter_by(OCode=patient_code).first()
    if not outpatient:
        patient = Patient.query.filter_by(Code=patient_code).first()
        if patient:
            new_outpatient = Outpatient(OCode=patient_code)
            new_outpatient.patient = patient
            # db.session.add(new_outpatient)
            # db.session.commit()
        
    #for op_detail table
    existing_op_detail = OpDetail.query.filter_by(OCode=patient_code, OP_visit=op_visit).first()
    if not existing_op_detail.op_detail:
        new_op_detail = OpDetail(OCode = patient_code, OP_visit=op_visit)
        # db.session.add(new_op_detail)
        # db.session.commit() 
        
    #for examine_attributes
    existing_examine_detail = ExamineDetail.query.filter_by(OCode=patient_code, 
                                                            OP_visit=op_visit, 
                                                            DoctorID=doctor_id,
                                                            Exam_datetime = exam_date).first()
    if not existing_examine_detail:
        new_examine_detail = ExamineDetail(
            OCode=patient_code,
            OP_visit=op_visit,
            DoctorID=doctor_id,
            Exam_datetime=exam_date,
            Next_datetime=next_date,
            Diagnosis=diagnosis,
            Fee=exam_fee
        )
        # db.session.add(new_examine_detail)
        # db.session.commit()

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
  
    inpatient_query = db.session.query(
            Patient, IpDetail, TreatAttribute
        ).join(
            Inpatient, Patient.Code == Inpatient.ICode
        ).join(
            IpDetail, Inpatient.ICode == IpDetail.ICode
        ).join(
            TreatAttribute, and_(
                IpDetail.ICode == TreatAttribute.ICode,
                IpDetail.IP_visit == TreatAttribute.IP_visit
            )
        ).filter(Patient.Code == input_id)

    outpatient_query = db.session.query(
            Patient, OpDetail, ExamineDetail
        ).join(
            Outpatient, Outpatient.OCode == Patient.Code  
        ).join(
            OpDetail, OpDetail.OCode == Outpatient.OCode  
        ).join(
            ExamineDetail, and_(
                ExamineDetail.OCode == OpDetail.OCode, 
                ExamineDetail.OP_visit == OpDetail.OP_visit 
            )
        ).filter(Patient.Code == input_id)


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
                "Admission_date": ip_detail.Admission_date,
                "Sickroom": ip_detail.Sickroom,
                "Discharge_date": ip_detail.Discharge_date,
                "Nurse_ID": ip_detail.Nurse_ID,
                "Fee": ip_detail.Fee,
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
    return jsonify(patient_list)


@actor.route('/export_inpatient_payment', methods=['GET'])
def export_inpatient_payment():
    patient_id = request.args.get('patient_id')
    ip_visit = request.args.get('ip_visit')  # This should be passed in the request
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    doctor_id = request.args.get('doctor_id')
    treatment_fee = request.args.get('treatment_fee')

    try:
        start_datetime = datetime.strptime(start_date, '%a, %d %b %Y %H:%M:%S %Z')
        end_datetime = datetime.strptime(end_date, '%a, %d %b %Y %H:%M:%S %Z')
    except ValueError as e:
        return jsonify({'error': 'Invalid date format'}), 400

    medication_usage = db.session.query(
        Use.MCode.label('use_mcode'), 
        Use.ICode.label('use_icode'),
        Use.IP_visit.label('use_ip_visit'),
        Use.DoctorID.label('use_doctor_id'),
        Use.Start_datetime.label('use_start_datetime'),
        Use.End_datetime.label('use_end_datetime'),
        Use.NumOfMed.label('use_num_of_med'),
        Medication.Code.label('medication_code'),
        Medication.Name.label('medication_name'),
        Medication.Price.label('medication_price'),
        Medication.Expired_Date.label('medication_expired_date')
    ).join(
        Medication, Use.MCode == Medication.Code
    ).filter(
        Use.ICode == patient_id,
        Use.IP_visit == ip_visit, 
        Use.DoctorID == doctor_id, 
        # If you're filtering by datetime, make sure you have converted the input strings to datetime objects
        Use.Start_datetime == start_datetime,
        Use.End_datetime == end_datetime
    ).all()

    medicine_list = []
    total_med_price = 0
    for use in medication_usage:
        # medication = Medication.query.get(use.MCode)
        medicine_info = {
            'code': use.use_mcode,
            'name': use.medication_name,
            "amount": use.use_num_of_med,
            "medication_name": use.medication_name,
            "medication_price": use.medication_price,
            "total_cost": use.use_num_of_med * use.medication_price
        }
        total_med_price += medicine_info['total_cost']
        medicine_list.append(medicine_info)

    total_cost = total_med_price + int(treatment_fee)

    # # Construct the report data
    report_data = {
        "medicine_list": medicine_list,
        "total_med_price": total_med_price,
        "total_cost": total_cost
    }
    return jsonify(report_data)


@actor.route('/export_outpatient_payment', methods=['GET'])
def export_outpatient_payment():
    patient_id = request.args.get('patient_id')
    op_visit = request.args.get('op_visit')  # This should be passed in the request
    exam_date = request.args.get('exam_date')
    doctor_id = request.args.get('doctor_id')
    examine_fee = request.args.get('examine_fee')

    try:
        exam_datetime = datetime.strptime(exam_date, '%a, %d %b %Y %H:%M:%S %Z')
    except ValueError as e:
        return jsonify({'error': 'Invalid date format'}), 400

    medication_usage = db.session.query(
        UseFor.MCode.label('usefor_mcode'), 
        UseFor.OCode.label('usefor_ocode'),
        UseFor.OP_visit.label('usefor_op_visit'),
        UseFor.DoctorID.label('usefor_doctor_id'),
        UseFor.Exam_datetime.label('usefor_exam_datetime'),
        UseFor.NumOfMed.label('usefor_num_of_med'),
        Medication.Code.label('medication_code'),
        Medication.Name.label('medication_name'),
        Medication.Price.label('medication_price'),
        Medication.Expired_Date.label('medication_expired_date')
    ).join(
        Medication, UseFor.MCode == Medication.Code
    ).filter(
        UseFor.OCode == patient_id,
        UseFor.OP_visit == op_visit, 
        UseFor.DoctorID == doctor_id, 
        # If you're filtering by datetime, make sure you have converted the input strings to datetime objects
        UseFor.Exam_datetime == exam_datetime
    ).all()

    medicine_list = []
    total_med_price = 0
    for usefor in medication_usage:
        # medication = Medication.query.get(use.MCode)
        medicine_info = {
            'code': usefor.usefor_mcode,
            'name': usefor.medication_name,
            "amount": usefor.usefor_num_of_med,
            "medication_name": usefor.medication_name,
            "medication_price": usefor.medication_price,
            "total_cost": usefor.usefor_num_of_med * usefor.medication_price
        }
        total_med_price += medicine_info['total_cost']
        medicine_list.append(medicine_info)

    total_cost = total_med_price + int(examine_fee)

    # # Construct the report data
    report_data = {
        "medicine_list": medicine_list,
        "total_med_price": total_med_price,
        "total_cost": total_cost
    }
    return jsonify(report_data)

@actor.route('/doctor')
def doctor():
    return render_template("doctor.html")

@actor.route('/nurse')
def nurse():
    return render_template("nurse.html")