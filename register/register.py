from register import register_bp
from flask import Blueprint,render_template, url_for, redirect, request
from flask_login import *
from home import *
from model import *
import openpyxl
from datetime import date
from sqlalchemy import *
from login import login_bpp
from flask_login import *
from flask_bcrypt import Bcrypt
bcrypt=Bcrypt()
import pandas as pd


@register_bp.route('/', methods=['POST', 'GET'])
def home():
    return render_template("/login/register.html")

@register_bp.route('/insertuser',methods=['POST'])
def insertuser():
    print("test")
    # Creazione di un utente
    try:
        print(request.form)
        nome=request.form['nome'],
        cognome=request.form['cognome'],
        password=bcrypt.generate_password_hash(request.form['email']+request.form['password']).decode('utf-8'),
        email=request.form['email'],
        areaManager = request.form['areaManager']
        ris = conn.execute(insert(utente).values(
            nome = nome,
            cognome=cognome,
            psw=password,
            email=email,
            areaManager = areaManager
            ))
        conn.commit()
        print(ris.inserted_primary_key[0])
        login_user(User(ris.inserted_primary_key[0],email[0])) # utilizzo flask_login per creare i cookies
        return redirect(url_for('home_bp.home'))
    except Exception as error:
        print("error")
        print(error)
        print(error.__cause__)
        conn.rollback()
    return redirect(url_for('register_bp.home'))

