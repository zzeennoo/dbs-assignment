from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)

@auth.route('/patient')
def patient():
    return render_template('patient.html')

@auth.route('/admin')
def admin():
    return render_template('admin.html')

@auth.route('/doctor_and_nurst')
def doctor_and_nurst():
    return render_template('doctor_and_nurst.html')