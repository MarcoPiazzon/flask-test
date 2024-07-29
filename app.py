from sqlalchemy import *
from flask_login import *
from flask import Flask,redirect,url_for,render_template,make_response, request
from home.home import home_bp
from login.login import login_bpp
from portafoglio.portafoglio import portafoglio_bp 
from calendario.calendario import calendario_bp
from contatto.contatto import contatto_bp
from trattativa.trattativa import trattativa_bp
from register.register import register_bp
from model import *
import datetime
import pandas
import openpyxl
app=Flask(__name__)
app.config['SECRET_KEY']='asd'

login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    print("sono dentro a load user")
    user = conn.execute(select(utente).where(utente.c.idutente==user_id)).fetchone()._asdict()
    return User(user_id,user['email'])

@app.context_processor
def inject_today_date():
    return {'today_date': datetime.date.today()}

app.register_blueprint(login_bpp,url_prefix='/login')
app.register_blueprint(home_bp,url_prefix='/home')
app.register_blueprint(portafoglio_bp, url_prefix='/portafoglio')
app.register_blueprint(calendario_bp, url_prefix='/calendario')
app.register_blueprint(contatto_bp, url_prefix='/contatto')
app.register_blueprint(trattativa_bp, url_prefix='/trattativa')
app.register_blueprint(register_bp, url_prefix='/register')


@app.route('/')
def main():
    return redirect(url_for('portafoglio_bp.home', idPort=current_user.idport, id=0))
    

@app.errorhandler(500)    
def error_handler(error):
        return render_template("/errors/500.html")

@app.errorhandler(404)
def error_handler(error):
    return render_template("/errors/404.html")

@app.errorhandler(401)
def error_handler(error):
    return render_template("/errors/401.html")
    
@app.errorhandler(403)
def error_handler(error):
    return render_template("/errors/403.html")

@login_required
@app.route('/appelli/<int:idapp>/users/download',methods=['POST'])
def userslistds(idapp):
    with app.test_client() as client:
        res =client.get('/esami/appelli/'+str(idapp)+'/users')
        content=res.data.decode('utf-8')
    pdf = HTML(string=content).write_pdf()
    respo= make_response(pdf)
    respo.headers['Content-Type'] = 'application/pdf'
    respo.headers['Content-Disposition'] = 'attachment; filename=risultati.pdf'
    return respo

if __name__ == "__main__":
    app.run(debug=True)
