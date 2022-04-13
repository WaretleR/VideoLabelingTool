import os
import json
import cv2

DATA_PATH = 'static'

class JSONCompatible():
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class ActionInfo(JSONCompatible):
    def __init__(self, type, start, end, id = -1, detection_conf = 1.0, tracking_conf = 1.0, classification_conf = 1.0, approved = True):
        self.id = id
        self.type = type
        self.start = start
        self.end = end
        self.detection_conf = detection_conf
        self.tracking_conf = tracking_conf
        self.classification_conf = classification_conf
        self.approved = approved
        self.framesDict = {}
        self.leftTopX = 10000
        self.leftTopY = 10000
        self.rightBottomX = 0
        self.rightBottomY = 0

    # TODO __str__

class VideoInfo(JSONCompatible):
    def __init__(self, videoName, pathToVideo = ''):
        self.name = '.'.join(videoName.split('.')[:-1])
        video = cv2.VideoCapture(os.path.join(pathToVideo, videoName))
        self.fps = video.get(cv2.CAP_PROP_FPS)
        self.w = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

class ActionStorage():
    def __init__(self, currentDataset = 'VIRAT'):
        self.currentDataset = currentDataset
        self.loadActions()
        self.loadNames()
    
    def loadActions(self):
        self.actions = {}
        for labelName in sorted(os.listdir(os.path.join(DATA_PATH, self.currentDataset, 'labels'))):
            videoName = labelName.split('.')[0]
            f = open(os.path.join(DATA_PATH, self.currentDataset, 'labels', labelName))
            label = f.read().split('\n')[:-1]
            f.close()
            label = [l.split(' ')[:-1] for l in label]
            label = [[int(l1) for l1 in l] for l in label]
                    
            for l in label:
                eventName = videoName + '.' + str(l[0])
                if videoName not in self.actions:
                    self.actions[videoName] = {}
                if eventName not in self.actions[videoName]:
                    self.actions[videoName][eventName] = ActionInfo(l[1], l[3], l[4], id = l[0])
                self.actions[videoName][eventName].framesDict[l[5]] = [e for e in l[6:]]
        for v in self.actions:
            self.actions[v] = list(self.actions[v].values())

    def loadNames(self):
        self.names = []
        for videoName in sorted(os.listdir(os.path.join(DATA_PATH, self.currentDataset, 'videos'))):
            self.names.append(VideoInfo(videoName, os.path.join(DATA_PATH, self.currentDataset, 'videos')))

    def getActions(self, videoName = ''):
        if videoName:
            currentActions = []
            videoNamePrefix = '.'.join(videoName.split('.')[:-1])
            for k, v in self.actions.items():
                if v.video == videoNamePrefix:
                    currentActions.append(self.actions[k])
            return currentActions
        else:
            return self.actions

    def getNames(self):
        return self.names

    def update(self, currentDataset = ''):
        if currentDataset != '':
            self.currentDataset = currentDataset
        self.loadActions()
        self.loadNames()

    def addAction(self, videoName : str, action : ActionInfo):
        i = 0
        while (videoName.split('.')[0] + '.' + str(i)) in self.actions:
            i += 1
        eventName = videoName + '.' + str(i)       

        self.actions[eventName] = action

    def saveActions(self, data):
        for videoName in data:
            data[videoName] = sorted(data[videoName], key=lambda k: (k['id']))
            f = open(os.path.join(DATA_PATH, self.currentDataset, 'labels', videoName + '.txt'), 'w+')
            for action in data[videoName]:
                for frameNumber in sorted(action['framesDict'].keys()):
                    bbox = action['framesDict'][str(frameNumber)]
                    frameLine = ' '.join((str(action['id']), str(action['type']), str(int(action['end']) - int(action['start'])), str(action['start']), str(action['end']), frameNumber, str(int(bbox[0])), str(int(bbox[1])), str(int(bbox[2])), str(int(bbox[3])))) + ' \n'
                    f.write(frameLine)
            f.close()