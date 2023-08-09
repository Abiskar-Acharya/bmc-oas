import uuid
from flask import Flask,current_app, jsonify
from pymongo import MongoClient
import datetime

app = Flask(__name__)

client = MongoClient('localhost', 27017)

db = client.examinationDB

def get_all_users():
    users = db.users.find({"user_name": { "$nin": ["admin"] }}).sort("created_on",-1)
    current_app.logger.info(f"Gettting all users called from mongodb")
    return list(users)

def get_user(email):
  try:
    current_app.logger.info(f"Getting one user {email}")
    query = {"email":email}  
    user = db.users.find_one(query)
    if user:
     test_id = user.get("test_id")
     query = {"test_id":test_id}
     role = db.roles.find_one(query)
     user["role"] = role["role_name"]
     current_app.logger.info(f"user {user}")
    return user
  except Exception as e:
      current_app.logger.error(f"error {e}")
      return False
def add_new_user(full_name,user_name,email,password,role):
  try:
    query = {"email":email}
    user_exists = db.users.find_one(query)
    print(user_exists)
    if user_exists:
      return False
    else:
      current_app.logger.info("add new user called")
      id = str(uuid.uuid4())
      timestamp = datetime.datetime.now()
      query = {
        "_id":id,
        "user_id":id,
        "full_name":full_name,
        "user_name":user_name,
        "email":email,
        "password":password,
        "created_on":timestamp
      }
      current_app.logger.info(f"inserting in user collection q {query} ")
      db.users.insert_one(query)
      role_id = str(uuid.uuid4())
      query ={
        "_id":role_id,
        "role_id":role_id,
        "user_id":id,
        "role_name":role
      }
      current_app.logger.info(f"inserting in roles collection q {query} ")
      db.roles.insert_one(query)
      current_app.logger.info(f"user added successfully ")
      return True
  except Exception as e:
    current_app.logger.error(f"error : {e}") 
    return False       
  
def delete_user(user_id):
    try:
      current_app.logger.info(f"deleting {user_id}") 
      query = { "user_id":user_id}
      response1 = db.users.delete_one(query)
      response2 = db.roles.delete_one(query)
      current_app.logger.info(f"deleting {user_id} is successfull {response1,response2}")
      return True
    except Exception as e:
      current_app.logger.error(f"error {e}")  
      return False
    
def add_new_test(test_name,test_code,subject,date,time,duration,total_q,marks,negative_mark):
  try:
    current_app.logger.info(f"add_new_test called")
    id = str(uuid.uuid4())
    scheduled_on = datetime.datetime.combine(date,time)
    query = {
      "_id": id,
      "test_id": id,
      "test_name":test_name,
      "test_code":test_code,
      "subject":subject,
      "scheduled_on":scheduled_on,
      "duration":duration,
      "total_q":total_q,
      "passing_marks":marks,
      "negative_mark":negative_mark,
      "isActive":True 
    }
    current_app.logger.info(f"adding new test {query}")
    db.tests.insert_one(query)
    current_app.logger.info(f"Test added Successfully") 
    return True
  except Exception as e:
    current_app.logger.error(f"Error : {e}")  
    return False  
  
def get_active_test():
  try:
    tests = db.tests.find({"isActive":True}).sort("scheduled_on",-1)
    if tests:
      return list(tests)
    else:
      return False
  except Exception as e:
    current_app.logger.error(f"Error : {e}")  
    return False     
  
def all_tests():
    try:
      tests = db.tests.find().sort("scheduled_on",-1)
      if tests:
        return list(tests)
      else:
        return False
    except Exception as e:
      current_app.logger.error(f"Error : {e}")  
      return False 

def delete_test(test_id):
    try:
      current_app.logger.info(f"deleting {test_id}") 
      query = { "test_id":test_id}
      db.tests.delete_one(query)
      current_app.logger.info(f"deleting {test_id} is successfull")
      return True
    except Exception as e:
      current_app.logger.error(f"error {e}")  
      return False
        
        
def add_question(question_data):
  try:
    current_app.logger.info(f"adding question {question_data}") 
    query = question_data
    q_id = str(uuid.uuid4())
    query["_id"] = q_id
    query["q_id"] = q_id
    db.questions.insert_one(query)
    current_app.logger.info(f"added question {q_id} is successfull")
    return True
  except Exception as e:        
      current_app.logger.error(f"error {e}")  
      return False    

def get_question():
  try:
    current_app.logger.info(f"Gettting all questions called from mongodb")
    question = db.questions.find()
    current_app.logger.info(f"got all questions called from mongodb, {question}")
    return list(question)
  except Exception as e:        
      current_app.logger.error(f"error {e}")  
      return False  
    
def delete_question(q_id):
    try:
      current_app.logger.info(f"deleting question {q_id}") 
      query = { "q_id":q_id}
      db.questions.delete_one(query)
      current_app.logger.info(f"deleting question {q_id} is successfull")
      return True
    except Exception as e:
      current_app.logger.error(f"error {e}")  
      return False  
    
def update_question(q_id,data):
    try:
      current_app.logger.info(f"deleting question {q_id}") 
      query = {"q_id":q_id}
      db.questions.update_one(query,{"$set":data})
      current_app.logger.info(f"deleting question {q_id} is successfull")
      return True
    except Exception as e:
      current_app.logger.error(f"error {e}")  
      return False  
            

def get_question_for_test(test_id):
  try:
    current_app.logger.info(f"Gettting test questions called from mongodb")
    question = db.questions.find({"test_id":test_id})
    current_app.logger.info(f"got test questions called from mongodb, {question}")
    return list(question)
  except Exception as e:        
      current_app.logger.error(f"error {e}")  
      return False      