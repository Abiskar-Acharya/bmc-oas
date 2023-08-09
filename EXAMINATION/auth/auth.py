from flask import (
    Blueprint,
    flash,
    make_response,
    redirect,
    render_template,
    current_app,
    request,
    url_for,
    session,
    g,
)
from constants import ORGANIZATION_NAME
from mongoDB import mongodb

auth_bp = Blueprint(
    "auth_bp", __name__, template_folder="templates", static_folder="static"
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    try:
        current_app.logger.info("LOGIN ROUTE CALLED ")
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            if not email or not password:
                current_app.logger.info(f"empty fields: {email},{password}")
                error_msg = "Username or Password fields are empty"
                flash(error_msg)
                return redirect(url_for("auth_bp.login"))
            user = mongodb.get_user(email)
            if not user:
                error_msg = "Incorrect username or email"
                flash(error_msg)
                return redirect(url_for("auth_bp.login"))
            if session.get("session_id") or session.get("user_name"):
                session.pop("session_id", None)
                session.pop("user_name", None)
            if user and email == user.get("email"):
                if password == user.get("password"):
                    session["session_id"] = user.get("user_id")
                    session["user_name"] = user.get("user_name")
                    print("session")
                    g.user = user.get("user_name")
                    if user.get("role") == 'admin':
                       return redirect(url_for("admin_bp.admin"))
                    elif user.get("role") == 'staff' :
                        return "staff"
                    elif user.get("role") == 'student':
                        return "student"
                else:
                    error_msg = "Incorrect password"
                    flash(error_msg)
                    return redirect(url_for("auth_bp.login"))
      
        return render_template("login.html", ORGANIZATION_NAME=ORGANIZATION_NAME)
    except Exception as e:
        current_app.logger.error(f"EXCEPTION OCCURED : {e}")
        return render_template("internal_server_error.html")


@auth_bp.route("/logout")
def logout():
    current_app.logger.info("logout route called")
    if session.get("session_id") or session.get("user_name"):
      session["session_id"] = None
      session["user_name"] = None
      current_app.logger.info(f"session set to none : {session['user_name'], session['session_id']}")
    return redirect("admin_bp.admin")
