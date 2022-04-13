from email.policy import default
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask.json import JSONEncoder

from data_manager import ActionStorage, ActionInfo, VideoInfo

import os

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

currentDataset = 'VIRAT'
actionStorage = ActionStorage(currentDataset)
currentVideo = actionStorage.getNames()[0]

@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')

@app.route('/actions', methods=['GET', 'PUT'])
def all_actions():
    response_object = {'status': 'success'}

    if request.method == 'PUT':
        post_data = request.get_json()

        actionStorage.saveActions(post_data)

        actionStorage.update(currentDataset)
        #response_object['actions'] = actionStorage.getActions(request.args.get("video", default=''))

    else:
        response_object['actions'] = actionStorage.getActions(request.args.get("video", default=''))

    return jsonify(response_object)


@app.route('/videos', methods=['GET'])
def all_videos():
    response_object = {'status': 'success'}

    if request.method == 'GET':
        datasetName = request.args.get("dataset")
        if datasetName == currentDataset:
            response_object['names'] = actionStorage.getNames()
        else:
            # TODO all datasets should be loaded
            pass

    return jsonify(response_object)



class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (ActionInfo, VideoInfo)):
            return obj.__dict__
        return JSONEncoder.default(self, obj)

app.json_encoder = CustomJSONEncoder

if __name__ == '__main__':
    app.run()
    