# Google Forms
This implementation simply changes polis for a simple Google Form

# Requirements
Written in Python 3.9

cryptography==3.4.8
email-validator==1.1.3
Flask-Babel==2.0.0
Flask-Bootstrap==3.3.7.1
Flask-Login==0.5.0
Flask-Mail==0.9.1
Flask-Migrate==3.1.0
Flask-WTF==0.15.1
gunicorn==20.1.0
PyJWT==2.1.0
PyMySQL==1.0.2
python-dotenv==0.19.0

# Installation
The easiest way is to simply create a virtual environment using `pipenv` and installing the requirements. Gunicorn and PyMySQL are for server deployment which I've done using both nginx and gunicorn as a server. For most testing purposes the default flask server is more than enough.

# Configuration
Configuration is done through a `.env` file which has to include the following parameters:
```
FLASK_APP=<name of flask app>
MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME=<gmail account>
MAIL_PASSWORD=<gmail password>
```


