from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    exisitngDatasets = [
        {
            'name' : 'VIRAT',
            'path' : 'D:\Files\Datasets\VIRAT'
        }
    ]
    return render_template('index.html', title='Home', datasets=exisitngDatasets)

    
@app.route('/labeling')
def labeling():
    return render_template('labeling.html', title='Labeling')