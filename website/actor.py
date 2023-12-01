from flask import Blueprint, render_template
from . import db

actor = Blueprint('actor', __name__)

@actor.route('/patient')
def patient():
    return render_template('patient.html')

@actor.route('/admin')
def admin():
    return render_template('admin.html')

@actor.route('/doctor_and_nurst')
def doctor_and_nurst():
    return render_template('doctor_and_nurst.html')