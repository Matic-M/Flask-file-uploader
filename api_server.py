import os
import base64
from base64 import b64decode
from flask import Flask,request,jsonify
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token # create_access_token() makes JSON Web Tokens
from flask_jwt_extended import get_jwt_identity #get_jwt_identity to get identity of a JWT p. route
from flask_jwt_extended import jwt_required # jwt_required() protects routes
from flask_jwt_extended import JWTManager # storing and retrieving tokens
from flask_cors import CORS, cross_origin

import datetime



#UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mov', 'avi', 'mp4'}


#https://flask.palletsprojects.com/en/3.0.x/patterns/fileuploads/
#https://www.freecodecamp.org/news/rest-api-tutorial-rest-client-rest-service-and-api-calls-explained-with-code-examples/
#https://realpython.com/flask-javascript-frontend-for-rest-api/
# command >> export FLASK_APP=api_server.py => how to load the application
# command >> export FLASK_ENV=development => switch to development environment
# command >> flask run --host=0.0.0.0

app = Flask(__name__)#flask instance of my class
CORS(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwMzg0NDkzNSwianRpIjoiMzQxMGQwZjgtNWQ4Yi00NjkzLWIzNDMtYjE4NjJlNGQxYjcyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Im1hdGljIiwibmJmIjoxNzAzODQ0OTM1LCJleHAiOjE3MDM4NDg1MzV9.WWmnCl_Fd4OPsLg2nJoPH_kPqcCvuzAA8v7PabWbgH8"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(seconds=3600) # key expires after 1 hour
jwt = JWTManager(app)

#MySQL configuration
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]="mojavirtualka"
app.config["MYSQL_DB"]="db_potk"
app.config['UPLOAD_FOLDER'] = "/home/matic/POTK_PRJ/DATA"

mysql = MySQL(app)

@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
  return jsonify(err="Token expired"), 401

# route to authenticate users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():

  username = request.json.get("username", None)
  password = request.json.get("password", None)
  cur = mysql.connection.cursor()
  cur.execute(""" SELECT username, password FROM users WHERE username=%s and password=%s """,(username,password))
  rv = cur.fetchall()
  cur.close()
    #print(rv)
    #username_iz_db=rv[0][0]
    #geslo_iz_db=rv[0][1]
    
    # check in sql
  if not rv:
    return jsonify({"msg": "Bad username or password"}), 401

  access_token = create_access_token(identity=username)
  return jsonify(access_token=access_token)
    


#todo
#1. ta routa naj bo jwt token->done
#2. ustvarite funkcijo, ki preverja dovoljene
#tipe datotek (jpg, png, mov, avi,...)->done
#3. shrani video oz. sliko v bazo

# id, filename, pathP-procesirani, pathR.....surovi

def allowed_file(filename):
    if '.' in filename:
        extension = filename.rsplit('.', 1)[1].lower()
        print(f"File extension: {extension}")
        return extension in ALLOWED_EXTENSIONS
    return False



@app.route("/fileUpload", methods=['POST'])
@jwt_required()
def api_file_upload():
  file = None
  try:
    if(request.method == "POST"):
    # check if the post request has the file part
      file = request.files.get('datoteka')
      print(f"File: {file}")

    # empty file
      if not file:
        return "No file", 400
    # if file is present and has correct suffix
      if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) #full path to the file
        file.save(file_path)
      
      # Read binary content of the file
        with open(file_path, 'rb') as binary_file:
          binary_data = binary_file.read()
          binary_data_base64 = base64.b64encode(binary_data).decode('utf-8')
    
        
        cur = mysql.connection.cursor()
        sql = ("""INSERT INTO images (filename, pathR) VALUES (%s, %s)""")
        cur.execute(sql, (filename, binary_data_base64))
        mysql.connection.commit()
        cur.close()

        return "OK", 200     
               
  except Exception as e:
    print(f"Exception: {str(e)}")
    return f"Error: {str(e)}", 400
    

@app.route("/showFile", methods=['GET'])
@jwt_required()
def showFile():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""SELECT filename, pathR FROM images""")
        rv = cur.fetchall()
        cur.close()

        # utf-8 decoding
        decoded_files = []
        for filename, pathR in rv:
            decoded_files.append({"filename": filename, "pathR": base64.b64encode(pathR).decode('utf-8')})

        return jsonify(decoded_files), 200
    except Exception as e:
        print(f"Error: {str(e)}")
        return "Could not show files", 500


    


@app.route("/protected", methods=["GET"])
@jwt_required() 
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route("/database", methods=["GET"])
def wp_database():
	try:
		cur=mysql.connection.cursor()
		cur.execute(""" SELECT * FROM users """)
		rv=cur.fetchall()
		cur.close()
		return jsonify(rv), 200
	except:
		return "Bad request", 400


@app.route("/data", methods=['GET', 'POST'])
@jwt_required()
def data():
  if(request.method=='POST'):
    try:
      data=request.json
      ime=data.get('ime')
      print(ime)
      cur=mysql.connection.cursor()
      sql=("""INSERT INTO data(ime) VALUES(%s)""")
      cur.execute(sql,(ime))
      mysql.connection.commit()
      cur.close()
      return "OK", 200
    except:
      return "Bad request", 200
  if(request.method=='GET'):
    try:
      cur=mysql.connection.cursor()
      sql=("""SELECT * FROM data""")
      cur.execute(sql)
      rv=cur.fetchall()
      print(rv)
      cur.close()
      return jsonify(rv)
    except:
      return "Bad request", 200
        

@app.route("/podatki", methods=['GET', 'POST'])
@jwt_required()
def podatki():
  if (request.method == 'POST'):
    try:
      data=request.json
      username=data.get("username")
      password=data.get("password")
      naziv=data.get("naziv")
      print(data)
      cur = mysql.connection.cursor()
      sql=(""" INSERT INTO users(username,password,naziv) VALUES(%s,%s,%s)""")
      cur.execute(sql, (username,password,naziv))
      mysql.connection.commit() # database refresh, proti SQL Injection
      cur.close()
      return "OK", 200
    except:
      return "Bad request", 200
  if (request.method == 'GET'):
    try:
      cur = mysql.connection.cursor()
      sql=("""SELECT * FROM users """)
      cur.execute(sql)
      rv=cur.fetchall()
      print(rv)
      cur.close()
      
      return jsonify(rv)
    except:
      return "Bad request", 200
		

		
@app.route("/home", methods=['GET', 'POST'])
def wp_hello_home():
	try:
		if request.method == 'POST':
			value=request.form.get('value')
			return '''<h1>The language value is: {} <h1>'''.format(value)	
		return '''
			<form method='POST'>
				<div><label>Value:<input type="text" name="value"></label></div>
				<input type ="submit" value="submit">
			</form>	'''
		#return "<p> HelloWorld</p>", 200
	except:
		return "Bad request", 400

@app.route("/register", methods=['GET', 'POST'])
def register():
  try:
    if request.method == 'GET':
      return """
        <form name="loginform" action="/register" id="loginform" method="post">
              <p>
                  <label>Username<br>
                      <input type="text" name="username" id="username" class="input" value="" size="20" tabindex="10"></label>
              </p>
              <p>
                  <label>Password<br>
                      <input type="password" name="password" id="user_pass" class="input" value="" size="20"
                          tabindex="20"></label>
              </p>
              <p>
                  <label>Naziv<br>
                      <input type="naziv" name="naziv" id="naziv" class="input" value="" size="20" tabindex="20"></label>
              </p>
              <p class="submit">
                  <input type="submit" class="btn" name="wp-submit" id="wp-submit" value="Register" tabindex="100">
              </p>
          </form> """
    if request.method == 'POST':
      #data=request.json
      #username=data.get("username")
      #password=data.get("password")
      #naziv=data.get("naziv")
      data=request.form
      username=data.get("username")
      password=data.get("password")
      naziv=data.get("naziv")
      print(data)
      cur=mysql.connection.cursor()
      sql=("""INSERT INTO users(username,password,naziv) VALUES (%s,%s,%s) """)
      cur.execute(sql, (username,password,naziv))
      mysql.connection.commit()
      cur.close()
      return "OK", 200
  except:
    return "Bad request", 400




if __name__=='__main__':#ce se zazene main instanca naj zazene 0.0.0.0
	app.run(host="0.0.0.0")
