from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
app.config.from_object('config')

from App import views # putting the import at the end avoids a circular import error
