from flask import Flask, render_template
from timestamps import data


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', data=data)



