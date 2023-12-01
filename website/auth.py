
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .model import Patient
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')

        patient = Patient.query.filter_by(Phone_number=phone_number).first()

        if patient:
            if patient.Password == password:
                login_user(patient, remember=True)
                return redirect(url_for('actor.patient'))
            else:
                return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('auth.login'))

    return render_template("login.html")

@auth.route('/logout')
def logout():
    return render_template("login.html")

@auth.route('/sign-up')
def sign_up():

    return render_template("sign_up.html")