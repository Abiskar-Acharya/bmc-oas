from logging.handlers import RotatingFileHandler
from flask import Flask, flash, redirect, render_template, url_for,g
from auth.auth import auth_bp
from admin.admin import admin_bp
from student.student import student
from werkzeug.exceptions import HTTPException
from flask_login import LoginManager
from flask_session import Session
from mongoDB.mongodb import client,db
from flask_wtf import CSRFProtect
from mongoDB import mongodb


# app
app = Flask(__name__)
# csrf = CSRFProtect(app)
app.config["SECRET_KEY"] = "SHIV"
app.secret_key = 'secret'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(student)

@app.errorhandler(HTTPException)
def handle_exception(e):
    app.logger.info(f"error occured : {e}")
    if e.code ==  404:
       return redirect(url_for("auth_bp.login"))
    else:
       return render_template("internal_server_error.html")
    
@app.errorhandler(500)
def  page_not_found(e):
     app.logger.error(f"error : {e}")
     return render_template("internal_server_error.html") 
  
if __name__ == '__main__':
	app.run(debug=True)
 
