from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

from App import views # putting the import at the end avoids a circular import error
