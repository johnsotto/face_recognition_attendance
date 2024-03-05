from flask import Flask, render_template
from timestamps import data




flk = Flask(__name__)

@flk.route('/home')
def table():
    return render_template('index.html', data=data)

flk.run(debug=True)
