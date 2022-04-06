import os
import json

DATA_PATH = os.path.join('static', 'data')

class EventInfo():
    def __init__(self, type, start, end, detection_conf = 1.0, tracking_conf = 1.0, classification_conf = 1.0, approved = True, framesDict = {}):
        self.type = type
        self.start = start
        self.end = end
        self.detection_conf = detection_conf
        self.tracking_conf = tracking_conf
        self.classification_conf = classification_conf
        self.approved = approved
        self.framesDict = framesDict
        self.leftTopX = 10000
        self.leftTopY = 10000
        self.rightBottomX = 0
        self.rightBottomY = 0

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

class ActionStorage():
    def __init__(self):
        self.loadActions()

    def loadActions(self):
        self.actions = {}
        for labelName in sorted(os.listdir(os.path.join(DATA_PATH, 'labels'))):
            videoName = labelName.split('.')[0]
            f = open(os.path.join(DATA_PATH, 'labels', labelName))
            label = f.read().split('\n')[:-1]
            f.close()
            label = [l.split(' ')[:-1] for l in label]
            label = [[int(l1) for l1 in l] for l in label]
                    
            for l in label:
                eventName = videoName + '.' + str(l[0])
                if eventName not in self.actions:
                    self.actions[eventName] = EventInfo(l[1], l[3], l[4])
                self.actions[eventName].framesDict[l[5]] = [e for e in l[6:]]

    def getActions(self):
        return list(self.actions.values())

    def addAction(self, videoName : str, action : EventInfo):
        i = 0
        while (videoName.split('.')[0] + '.' + str(i)) in self.actions:
            i += 1
        eventName = videoName + '.' + str(i)       

        self.actions[eventName] = action