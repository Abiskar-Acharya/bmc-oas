
from flask import Blueprint, Flask, current_app, flash, redirect, render_template, request, session, url_for
from mongoDB import mongodb
from flask_paginate import Pagination, get_page_parameter,get_page_args
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,IntegerField,DateTimeField,SelectField,FloatField,TextAreaField,DateField,TimeField
from wtforms.validators import DataRequired,InputRequired

admin_bp = Blueprint("admin_bp",__name__,template_folder="templates",static_folder="static")
class searchForm(FlaskForm):
    search = StringField("Search")
    
class TestForm(FlaskForm):
    test_name = StringField("Test name",validators=[InputRequired()])
    test_code = StringField("Test code",validators=[InputRequired()])
    subject = StringField("subject",validators=[InputRequired()])
    date= DateField("Schedule Date",validators=[InputRequired()])
    time= TimeField("Schedule time",validators=[InputRequired()])
    duration = SelectField("Duration",validators=[InputRequired()],choices=[('30', '30 MIN'), ('1', '1 hour'), ('2', '2 hour'), ('3', '3 hour')])
    total_q = IntegerField("Total Questions",validators=[InputRequired()])
    marks =  FloatField("passing Marks",validators=[InputRequired()])
    negative_mark =  FloatField("Negative Mark",validators=[InputRequired()])
    # submit = SubmitField("Add")
 
class QuestionForm(FlaskForm):
    tests = mongodb.all_tests() 
    choices = []
    for test in tests:
       choices.append((test.get('test_id'),test.get("test_name")))  
    test = SelectField("Select Test",validators=[InputRequired()],choices=choices)     
    question = TextAreaField("Question",validators=[InputRequired()])
    a = StringField("A",validators=[InputRequired()])
    b = StringField("B",validators=[InputRequired()])
    c = StringField("C",validators=[InputRequired()])
    d = StringField("D",validators=[InputRequired()])
    correct_ans =  SelectField("Correct Answer",validators=[InputRequired()],choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')])
    
def get_users(users,offset=0,per_page=3):
    return users[offset:offset+per_page]

def get_search(users,search):
   search_results = [] 
   for user in users:
       if user.get("user_name"):
        if search in user.get("user_name"):
            search_results.append(user)  
   return search_results 

def search_test(tests,key):
    search_results = []
    for test in tests:
        if key in test.get("test_name"):
            search_results.append(test)
    return search_results
            
@admin_bp.route("/admin")
def admin():
    if not session.get("session_id"):
        return redirect(url_for("auth_bp.login"))
        
    return render_template("admin.html")

@admin_bp.route("/set-test",methods=["GET","POST"])
def set_test():
    if not session.get("session_id"):
        return redirect(url_for("auth_bp.login"))
    current_app.logger.info("set test function started")
    searchform = searchForm()
    form = TestForm()
    if request.method == "POST":
        req = request.form 
        current_app.logger.info("Post request call")
        if form.is_submitted() and req.get("Add") :
            current_app.logger.info("new test adding process initiated")
            if form.validate_on_submit():
                test_name = form.test_name.data
                test_code = form.test_code.data
                subject = form.subject.data
                date= form.date.data
                time= form.time.data
                duration = form.duration.data
                total_q = form.total_q.data
                marks = form.marks.data
                negative_mark = form.negative_mark.data
                add_state = mongodb.add_new_test(test_name=test_name,
                                                 test_code=test_code,
                                                 subject=subject,
                                                 date=date,
                                                 time=time,
                                                 duration=duration,
                                                 total_q=total_q,
                                                 marks=marks,
                                                 negative_mark=negative_mark)
                if add_state:
                    message = "Test Added Successfully"
                    flash(message,"success")
                else:
                    message = "Adding test failed"
                    flash(message,"danger")
    current_app.logger.info("getting tests from db")
    tests = mongodb.all_tests()
    page = int(request.args.get("page",1))
    per_page = 3
    offset = (page - 1)*per_page 
    search_keyword = "" 
    if request.args.get("search"):
        current_app.logger.info("search initiated from search bar")
        search_keyword = request.args.get("search")
        search_results = search_test(tests,search_keyword)
        found = len(search_results)
        current_app.logger.info(f"results found {found}, {search_keyword} , {search_results}")
        search_results_tests = get_users(search_results,offset=offset,per_page=per_page)
        total = len(search_results)
        pagination = Pagination(page=page,per_page=per_page,total=total,search=True,found=found)
        return render_template("set_test.html",form=form,
                        page=page,
                        per_page=per_page,        
                        tests=search_results_tests,
                        pagination=pagination,
                        searchform=searchform,
                        search_keyword=search_keyword
                        )                    
    total = len(tests)
    pagination = Pagination(page=page,per_page=per_page,total=total) 
    pagination_tests = get_users(tests,offset=offset,per_page=per_page)         
    return render_template("set_test.html",form=form,
                        tests=pagination_tests,
                        page=page,
                        per_page=per_page,
                        pagination=pagination,
                        searchform=searchform,
                        search_keyword=search_keyword
                        ) 
    
             
    

@admin_bp.route("/question-inventory")
def question_inventory():
    return render_template("question_inventory.html")

@admin_bp.route("/update-test")
def update_test():
    return render_template("update_test.html")

@admin_bp.route("/view-test")
def view_result():
    return render_template("view_results.html")


@admin_bp.route("/add-user",methods=["GET","POST","PUT"])
def add_user():
    if not session.get("session_id"):
        return redirect(url_for("auth_bp.login"))
    current_app.logger.info("add user called")
    full_name = ""
    user_name = ""
    email = ""
    if request.method == "POST":  
      req = request.form
      current_app.logger.info(f"request {req}")
      if request.form.get("full_name") and request.form.get("user_name") and request.form.get("email") and  request.form.get("password") and not request.form.get('search'):
            print("inside")
            current_app.logger.info(f"adding user in db started {req}")  
            full_name = request.form.get("full_name")
            user_name = request.form.get("user_name")
            email = request.form.get("email")
            password = request.form.get("password")
            role = ""
            if request.form.get("student"):
                role = "student"
            elif request.form.get("staff"):
                role = "staff"
            if mongodb.add_new_user(full_name,user_name,email,password,role):
                msg = "User Added Successfully" 
                flash(msg,"success")  
                redirect(url_for("admin_bp.add_user"))
            else :
                msg = "Adding user failed or Email already exists" 
                flash(msg,"danger")
                redirect(url_for("admin_bp.add_user"))
      else:
          if not request.form.get('search'):
            msg = "Some fields are empty"
            flash(msg,"danger")        
    current_app.logger.info("getting all user called") 
    users = mongodb.get_all_users()
    current_app.logger.info(users)
    searchActive = False
    search = ""
    search_result = [] 
    page = int(request.args.get("page",1))
    per_page = 3
    offset = (page - 1)*per_page
    if request.form.get("search") and not request.form.get("search") == "":
        searchActive = True
        search = request.form.get("search")
        search_result= get_search(users,search)
        print(search_result)
        found = len(search_result)
        search_result_users = get_users(search_result,offset=offset,per_page=per_page)
        total = len(search_result_users)
        pagination = Pagination(page=page,per_page=per_page,total=total,search=searchActive,found=found)
        return render_template("add_user.html",
                           users=search_result_users,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           search=search,
                           full_name=full_name,
                           user_name=user_name,
                           email=email
                           )
    else:   
        total = len(users)
        pagination = Pagination(page=page,per_page=per_page,total=total)
        pagination_users = get_users(users,offset=offset,per_page=per_page)    
        return render_template("add_user.html",
                           users=pagination_users,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           search=search,
                           full_name=full_name,
                           user_name=user_name,
                           email=email
                           )

@admin_bp.route("/delete-user/<string:id>")
def delete_user(id):
  try:
    if not session.get("session_id"):
        return redirect(url_for("auth_bp.login"))    
    current_app.logger.info(f"Delete user called, user {id}")
    mongodb.delete_user(id)
    current_app.logger.info(f"Deleting user sucessfull, user {id}")
    return redirect(url_for("admin_bp.add_user"))
  except Exception as e:
     current_app.logger.error(f"error : {e}")

@admin_bp.route("/delete-test/<string:id>")
def delete_test(id):
  try:
    if not session.get("session_id"):
        return redirect(url_for("auth_bp.login"))    
    current_app.logger.info(f"Delete test called, test {id}")
    mongodb.delete_test(id)
    current_app.logger.info(f"Deleting test sucessfull, test {id}")
    return redirect(url_for("admin_bp.set_test"))
  except Exception as e:
     current_app.logger.error(f"error : {e}")



@admin_bp.route("/add-questions", methods=["GET","POST"])
def add_questions():
  try:
    print(request.args)
    all_tests = mongodb.all_tests()
    question_type = request.args.get("type")
    test_name = request.args.get("test_name")
    Add_blank = request.args.get("Add_blank")  
    no_of_blanks = request.args.get("no_of_blank")
    blanks = {}
    if no_of_blanks:
        for i in range(int(no_of_blanks)):
            name = f"blank_{str(i+1)}"
            value = ""
            if request.args.get(name):
                value = request.args.get(name)
                
            blanks[name] ={"name":name,
                         "value":value} 
    no_of_tables =  request.args.get("no_of_tables")        
    tables = []
    headers = {}
    table_datas = {}
    if no_of_tables:
        for i in range(int(no_of_tables)):
            table_name = f"table_{str(i+1)}"
            table_row_name = f"{table_name}_row"
            table_col_name = f"{table_name}_col"
            table_rows = ""
            table_col = ""
            table_data = { 
                            "name":table_name,
                            "table_row_name":table_row_name,
                            "table_col_name":table_col_name,
                            "table_rows":table_rows,
                            "table_col":table_col
                            }
            if request.args.get(table_row_name):
                table_data["table_rows"]=request.args.get(table_row_name)
                table_rows = request.args.get(table_row_name)
            if request.args.get(table_col_name):
                table_data["table_col"] = request.args.get(table_col_name)
                table_col = request.args.get(table_col_name)
                data_recived = dict(request.args)
                for j in range(int(table_col)):
                    for key,val in data_recived.items():
                        header_recived = f"{table_name}_header_{j}"
                        if header_recived == key:
                            if not val:
                              headers[str(key)] = ""
                            else:     
                              headers[str(key)] = str(val)
                              
                for k in range(int(table_rows)):
                    for l in range(int(table_col)):
                          search = f"{table_name}_{k}{l}"
                          print(search, data_recived.get(search))
                          if data_recived.get(search):
                              table_datas[search] = data_recived.get(search)        
                              print("innnnnnnnn",search, key, data_recived.get(search))
                                
                
            tables.append(table_data)  
    question_i=request.args.get("question_i")
    a = request.args.get("a")
    b = request.args.get("b")
    c = request.args.get("c")
    d = request.args.get("d")           
    print("-------------------",tables)  
    print("000000000000",headers)
    print("++++++++++++++",table_datas)
    new_q = []
    if question_i:
     new_q = question_i.split("*") 
    print(new_q)
    print(blanks)
    mark = request.args.get("mark")
    correct_answer = request.args.get("correct_answer")
    question_data = {
        "test_name":test_name,
        "question_type":question_type,
        "mark":mark,
        "question":question_i,
        "options":[a,b,c,d],
        "correct_answer":correct_answer,
         "blank_data": blanks,
         "table_data":{
             "headers":headers,
             "table_datas":table_datas,
             "tables":tables
         } 
    }
    save_question = request.args.get("save_question")
    if save_question:
      insert_status = mongodb.add_question(question_data)
      if insert_status:
          current_app.logger.info("inserted successfully") 
          flash("question saved successfully","success")
      else:
          current_app.logger.info("not inserted")
          flash("error saving question")    
    return render_template("add_questions.html",
                           all_tests=all_tests,
                           question_type=question_type,
                           test_name=test_name,
                           Add_blank=Add_blank,
                           no_of_blanks=no_of_blanks,
                           blanks=blanks,
                           no_of_tables=no_of_tables,
                           tables=tables,
                           headers=headers,
                           table_datas=table_datas,
                           question_i=question_i,
                           a=a,
                           b=b,
                           c=c,
                           d=d,
                           new_q=new_q,
                           mark=mark
                           ) 
   
  except Exception as e:
     current_app.logger.error(f"error : {e}")

# @admin_bp.route("set-question-type")
# def set_question_type():
    