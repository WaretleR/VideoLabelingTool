from flask import Flask, jsonify, request
from flask_cors import CORS
from flask.json import JSONEncoder

from data_manager import ActionStorage, EventInfo

import os

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

actionStorage = ActionStorage()
currentVideo = 'VIRAT_S_010204_04_000646_000754.mp4'

@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/actions', methods=['GET', 'POST'])
def all_actions():
    response_object = {'status': 'success'}

    if request.method == 'POST':
        post_data = request.get_json()

        actionStorage.addAction(currentVideo, {
            'type': post_data.get('type'),
            'start' : post_data.get('start'),
            'end' : post_data.get('end'),
            'detection_conf' : 1.0,
            'tracking_conf' : 1.0,
            'classification_conf' : 1.0,
            'approved' : True,
            'selected' : False,
            'framesDict': {}
        })

    else:
        response_object['actions'] = actionStorage.getActions()

    print(response_object['actions'])
    return jsonify(response_object)


@app.route('/videos', methods=['GET'])
def all_videos():
    response_object = {'status': 'success'}

    if request.method == 'GET':
        videoName = request.args.get("name")
        response_object['videoPath'] = os.paht.join('videos', videoName + '.mp4')


    return jsonify(response_object)



class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, EventInfo):
            return obj.__dict__
        return JSONEncoder.default(self, obj)

app.json_encoder = CustomJSONEncoder

if __name__ == '__main__':
    app.run()
    