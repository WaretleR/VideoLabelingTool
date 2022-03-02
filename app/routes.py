from flask import render_template
from app import app
import os

def getFirstVideoName(basePath : str) -> str:
    datasetPath = os.path.join("static", "datasets", basePath, "videos")
    for vName in os.listdir(datasetPath):
        return vName
        
@app.route('/')
@app.route('/index')
def index():
    exisitngDatasets = [
        {
            'name' : 'VIRAT',
            'path' : 'VIRAT',
            'first_video' : getFirstVideoName('VIRAT')
        },
        {
            'name' : 'Kinetics-600',
            'path' : 'Kinetics',
            'first_video' : getFirstVideoName('Kinetics')
        }
    ]
    return render_template('index.html', title='Home', datasets=exisitngDatasets)

    
@app.route('/labeling/<datasetFolder>/<videoName>')
def labeling(datasetFolder, videoName=''):
    datasetPath = os.path.join("static", "datasets", datasetFolder, "videos")

    videoNames = []
    for i, vName in enumerate(os.listdir(datasetPath)):
        if i == 0 and videoName == '':
            videoName = vName
        videoNames.append(vName)
    videoPath = "datasets/" + datasetFolder + "/videos/" + videoName
    return render_template('labeling.html', title='Labeling', dataset = datasetFolder, video_path=videoPath, video_names=videoNames)