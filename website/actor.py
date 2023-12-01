from flask import Blueprint, render_template
from . import db
from flask_login import login_required, current_user

actor = Blueprint('actor', __name__)

@login_required
@actor.route('/patient')
def patient():
    return render_template('patient.html')

@actor.route('/admin')
def admin():
    return render_template('admin.html')

@actor.route('/doctor_and_nurse')
def doctor_and_nurse():
    return render_template('doctor_and_nurse.html')