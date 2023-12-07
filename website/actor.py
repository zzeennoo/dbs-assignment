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

    print("Number of elements in patient_list:", len(patient_list))
    print("Treatment type of the first element in patient_list:", patient_list[0]['phone_number'])

    return jsonify(patient_list)


@actor.route('/export_inpatient_report', methods=['GET'])
def export_inpatient_report():
    patient_id = request.args.get('patient_id')
    ip_visit = request.args.get('ip_visit')  # This should be passed in the request

    # Query to get patient details
    patient = Patient.query.get(patient_id)

    # Query to get medication usage for this inpatient treatment
    medication_usage = db.session.query(Use, Medication).join(
        Medication, Use.MCode == Medication.Code
    ).filter(
        Use.ICode == patient_id,
        Use.IP_visit == ip_visit
    ).all()

    # Calculate the total medication cost
    medication_cost = sum(
        use.NumOfMed * medication.Price for use, medication in medication_usage
    )

    # Get the treatment fee (assuming it's stored in IpDetail or similar)
    treatment_fee = IpDetail.query.filter_by(
        ICode=patient_id, 
        IP_visit=ip_visit
    ).first().Fee

    # Construct the medication details list for the report
    medication_details = [{
        "code": medication.Code,
        "name": medication.Name,
        "price": medication.Price,
        "amount": use.NumOfMed,
        "total_cost": use.NumOfMed * medication.Price
    } for use, medication in medication_usage]

    # Construct the report data
    report_data = {
        "patient_name": patient.First_Name + " " + patient.Last_Name,
        "patient_id": patient_id,
        "phone_number": patient.Phone_number,
        "admission_date": patient.inpatients[0].Admission_date.strftime("%Y-%m-%d"),  # Assuming inpatients is a list
        "billing_date": "...",  # You will need to provide this
        "treatment_fee": treatment_fee,
        "medication_details": medication_details,
        "total_cost": treatment_fee + medication_cost
    }

    return jsonify(report_data)

    patient_id = request.args.get('patient_id')
    ip_visit = request.args.get('ip_visit')  # Assuming this is needed to identify the treatment

    # Fetch patient and treatment details
    patient = Patient.query.get(patient_id)
    treatment = IpDetail.query.filter_by(ICode=patient_id, IP_visit=ip_visit).first()
    medicine_uses = Use.query.filter_by(ICode=patient_id, IP_visit=ip_visit).all()
    
    # Construct the medicine list and calculate the total price
    medicine_list = []
    total_price = 0
    for use in medicine_uses:
        medication = Medication.query.get(use.MCode)
        medicine_info = {
            'code': medication.Code,
            'name': medication.Name,
            'price': medication.Price,
            'amount': use.NumOfMed,
            'total_cost': use.NumOfMed * medication.Price
        }
        total_price += medicine_info['total_cost']
        medicine_list.append(medicine_info)
    
    # Prepare the report data
    report_data = {
        'patient_name': patient.First_Name + ' ' + patient.Last_Name,
        'patient_id': patient_id,
        # ... other patient details ...
        'treatment_fee': treatment.Fee if treatment else 0,
        'medicine_list': medicine_list,
        'total_price': total_price
    }

    return jsonify(report_data)



@actor.route('/doctor')
def doctor():
    return render_template("doctor.html")

@actor.route('/nurse')
def nurse():
    return render_template("nurse.html")