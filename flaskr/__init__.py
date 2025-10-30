from flask import Flask

app = Flask(__name__)

#TODO: Research how to setup a proper secret key for 
#this project and then move this to a config file
app.secret_key = "you-will-never-guess"

from flaskr import routes