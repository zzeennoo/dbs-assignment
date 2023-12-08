
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .model import Patient, Employee, Doctor, Nurse, PhoneNumber
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/patient-login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')

        patient = Patient.query.filter_by(phone_number = phone_number).first()

        if patient:
            if patient.password == password:
                login_user(patient, remember=True)
                return redirect(url_for('actor.patient'))
            else:
                return redirect(url_for('auth.patient_login'))
        else:
            return redirect(url_for('auth.patient_login'))

    return render_template("loginPatient.html")

@auth.route('/doctor-login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        
        doctor = Doctor.query.join(Employee, Doctor.DoctorID == Employee.EmployeeID)\
                             .join(PhoneNumber, Employee.EmployeeID == PhoneNumber.EmployeeID)\
                             .filter(PhoneNumber.Phone_no == phone_number).first()
        
        first_employee = db.session.query(Employee).first()
        if first_employee:
            print("First Name:", first_employee.First_Name)
            print("Last Name:", first_employee.Last_Name)

            full_name = f"{first_employee.First_Name} {first_employee.Last_Name}"
            print("Full Name:", full_name)
        else:
            print("No employees found.")

        if doctor:
            if doctor.employee.Password == password:
                login_user(doctor.employee, remember=True)
                return redirect(url_for('actor.doctor'))
            else:
                return redirect(url_for('auth.doctor_login'))
        else:
            return redirect(url_for('auth.doctor_login'))

    return render_template("loginDoctor.html")

# @auth.route('/login_for_admin', methods=['GET', 'POST'])
# def login_for_admin():
#     if request.method == 'POST':
#         name_input = request.form.get('name')
        
#         password_input = request.form.get('password')
#         print(name_input)
#         print(password_input)

#         # nurse = Nurse.query.join(Employee, Nurse.NurseID == Employee.EmployeeID)\
#         #                    .join(PhoneNumber, Employee.EmployeeID == PhoneNumber.EmployeeID)\
#         #                    .filter(PhoneNumber.Phone_no == phone_number).first()

#         # if nurse:
#         #     if nurse.employee.Password == password:
#         #         login_user(nurse.employee, remember=True)
#         #         return redirect(url_for('actor.nurse'))
#         #     else:
#         #         return redirect(url_for('auth.nurse_login'))
#         # else:
#         #     return redirect(url_for('auth.nurse_login'))
#         if name_input == "admin" and password_input == "pass123":
#             redirect(url_for('actor.admin'))
#         else:
#             print(name_input)
#     print("incorrect password")

#     return redirect(url_for('auth.login_for_admin'))

@auth.route('/login_for_admin', methods=['GET', 'POST'])
def login_for_admin():
    if request.method == 'POST':
        name_input = request.form.get('name')
        password_input = request.form.get('password')

        if name_input == "admin" and password_input == "pass123":
            return redirect(url_for('actor.admin'))
        else:
            print("Incorrect password")  # This line is executed when the password is incorrect

    return render_template('loginNurse.html')