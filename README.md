# Flask-file-uploader

Flask-based web application allows users to create accounts and login, upload files, and interact with data through a RESTful API. The system leverages JWT for secure user authentication and stores uploaded files in a MySQL database in BLOB (Binary Large Object) format.

## Instructions

* create virtual environment
```bash
python -m venv venv
```
* activate virtual environment
```bash
source venv/bin/activate
```

* clone this repository
```bash
git clone https://github.com/Matic-M/Flask-file-uploader
````

* inside folder make another folder called DATA and change path in api_server.py!!!

* install requirements
```bash
pip install -r requirements.txt
```

* export variables and run flask on all adresses (port 5000 by default)
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0
````

* login and create MySQL database
```bash
mysql -u root -p
```

```bash
CREATE DATABASE my_database;
```

* use database
```bash
USE my_database;

* create table users
```bash
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL,
    password VARCHAR(80) NOT NULL,
    naziv VARCHAR(100) NOT NULL
);
```

* create table photos
```bash
CREATE TABLE photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(100) NOT NULL,
    pathR LONGBLOB NOT NULL
);
```

* test endpoints with curl and don't forget on JWT token
