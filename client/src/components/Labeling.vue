<template class="parent">
    <div class="labeling" ref="labeling">
        <video-player class="video-player-box" ref="videoPlayerBox" :video-path='currentVideoPath'></video-player>
        
        <div class="frame-label">
            <label for="frameInput">Кадр:</label>
            <input type="number" id="frameInput" v-model="desiredFrame" @input="seekToFrame">
        </div>

        <div class="video-select">
            <div v-for="video in videoInfo" :key="video.name">
                <b-button
                    @click="updateVideo(video)"
                    :pressed="video.name == currentVideoInfo.name"
                    class="btn-success btn-sm w-100" style="word-wrap: break-word">
                        {{ video.name }}
                </b-button>
            </div>
        </div>

        <div class="row">
            <div class="col">
                <h3>Actions</h3>
                <hr>

                <b-alert :variant="alertVariant" :show="showAlert">{{ alertMessage }}</b-alert>
                
                <b-button variant="success" @click="saveDataset">Save</b-button>
                <br><br>

                <div class="table-container">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th scope="id">ID</th>
                                <th scope="col">Class</th>
                                <th scope="col">Start</th>
                                <th scope="col">End</th>
                                <th scope="col">D</th>
                                <th scope="col">T</th>
                                <th scope="col">C</th>
                                <th scope="col">
                                    <b-button variant="primary" class="w-100" @click="selectAll">Select</b-button>
                                    <b-button variant="outline-primary" class="w-100" @click="deselectAll">Deselect</b-button>
                                </th>
                                <th scope="col"></th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(action, index) in actions[currentVideoInfo.name]" :key="index">
                                <td>{{ action.id }}</td>
                                <td>{{ action.type }}</td>
                                <td>{{ action.start }}</td>
                                <td>{{ action.end }}</td>
                                <td>{{ action.detection_conf }}</td>
                                <td>{{ action.tracking_conf }}</td>
                                <td>{{ action.classification_conf }}</td>
                                <td>
                                    <b-button variant="outline-primary" class="w-100" :pressed.sync="action.selected" @click="updateVisibleBbox">Select</b-button>
                                    <b-button variant="outline-success" class="w-100" :pressed.sync="action.approved">Approve</b-button>
                                </td>
                                <td>
                                    <b-button variant="light" class="w-100" v-b-modal.manage-modal @click="updateAction(action, index)">Manage</b-button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <b-modal ref="manageModal"
            id="manage-modal"
            title="Manage action..."
            hide-footer>
            <b-form @submit="onSubmit" @reset="onReset" @ class="w-100">
                <b-form-group id="form-class-group"
                                            label="Class:"
                                            label-for="form-class-input">
                    <b-form-input id="form-class-input"
                                                type="text"
                                                v-model="manageForm.type"
                                                required
                                                placeholder="Class...">
                    </b-form-input>
                </b-form-group>

                <b-form-group id="form-start-group"
                                            label="First frame:"
                                            label-for="form-start-input">
                    <b-form-input id="form-start-input"
                                                type="number"
                                                v-model="manageForm.start"
                                                required
                                                placeholder="First frame...">
                    </b-form-input>
                </b-form-group>
                <b-form-group id="form-end-group"
                                            label="Last frame:"
                                            label-for="form-end-input">
                    <b-form-input id="form-end-input"
                                                type="number"
                                                v-model="manageForm.end"
                                                required
                                                placeholder="Last frame...">
                    </b-form-input>
                </b-form-group>
                    

                <b-button type="submit" variant="primary">Update</b-button>
                <b-button type="reset" variant="danger">Delete</b-button>
            </b-form>
        </b-modal>

        <selection class="labeling-box" ref="draw"></selection>

    </div>
</template>

<script>
import axios from 'axios';
import Vue from 'vue';
import VideoPlayer from './VideoPlayer.vue'
import Alert from './Alert.vue';

class Action {
    constructor(type, start, end, id) {
        this.id = id;
        this.type = type;
        this.start = start;
        this.end = end;
        this.detection_conf = 1.0;
        this.tracking_conf = 1.0;
        this.classification_conf = 1.0;
        this.approved = true;
        this.selected = true;
        this.framesDict = {};
    }
}

Vue.component('selection', {
    template: "<canvas id='canvas' ref='select' @mousedown='processMouseDown' @mousemove='processMouseMove' @mouseup='processMouseUp'></canvas>",
    data() {
        return {
            canvas: null,
            ctx: null,
            collisionEps: 10,
            currentFrame: 0,
            videoName: '',
            w: 0,
            h: 0,
            actions: [],
            bboxIdx: [],
            resizeMode: false,
            resizedIdx: 0,
            resizeStartSize: {
                x: 0,
                y: 0
            },
            resizeConfig: {
                x: 0,
                y: 0
            },
            startPosition: {
                x: null,
                y: null,
            },
            transitionalBbox: {}
        };
    },

    methods: {

        processMouseDown(e) {
            if (document.getElementById('video-html-player').paused || document.getElementById('video-html-player').ended)
            {
                this.startPosition.x = e.clientX - canvas.offsetLeft;
                this.startPosition.y = e.clientY - canvas.offsetTop;

                let col = this.detectCollision(this.startPosition);
                this.resizeMode = true;
                if (col.x == 0 && col.y == 0) {
                    this.actions[this.videoName].push(new Action(0, this.currentFrame, this.currentFrame, this.getNewActionID()));
                    this.resizedIdx = Object.keys(this.actions[this.videoName]).length - 1;
                    Vue.set(this.actions[this.videoName][this.resizedIdx].framesDict, this.currentFrame, [this.startPosition.x / this.canvas.width * this.w, this.startPosition.y / this.canvas.height * this.h, 0, 0]);
                    this.bboxIdx.push(this.resizedIdx);
                }
                else {
                    if (!this.actions[this.videoName][col.idx].framesDict.hasOwnProperty(this.currentFrame)) {
                        Vue.set(this.actions[this.videoName][col.idx].framesDict, this.currentFrame, this.transitionalBbox[col.idx]);
                    }
                    this.resizeStartSize.x = this.actions[this.videoName][col.idx].framesDict[this.currentFrame][2] / this.w * this.canvas.width;
                    this.resizeStartSize.y = this.actions[this.videoName][col.idx].framesDict[this.currentFrame][3] / this.h * this.canvas.height;
                    this.resizedIdx = col.idx;
                }
                this.resizeConfig.x = col.x;
                this.resizeConfig.y = col.y;
            }
        },

        processMouseMove(e) {
            if (this.resizeMode) {
                let mouseDelta = {
                    x : e.clientX - canvas.offsetLeft - this.startPosition.x,
                    y : e.clientY - canvas.offsetTop - this.startPosition.y,
                };

                // first - change bbox which is being resized

                if (this.resizeConfig.x > 0)
                {
                    this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][2] = (this.resizeStartSize.x + mouseDelta.x) / this.canvas.width * this.w; 
                }
                else if (this.resizeConfig.x < 0)
                {
                    this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][0] = (this.startPosition.x + mouseDelta.x) / this.canvas.width * this.w; 
                    this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][2] = (this.resizeStartSize.x - mouseDelta.x) / this.canvas.width * this.w; 
                }

                if (this.resizeConfig.y > 0)
                {
                    this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][3] = (this.resizeStartSize.y + mouseDelta.y) / this.canvas.height * this.h; 
                }
                else if (this.resizeConfig.y < 0)
                {
                    this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][1] = (this.startPosition.y + mouseDelta.y) / this.canvas.height * this.h; 
                    this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][3] = (this.resizeStartSize.y - mouseDelta.y) / this.canvas.height * this.h; 
                }
                
                if (this.resizeConfig.x == 0 && this.resizeConfig.y == 0)
                {
                    this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][2] = mouseDelta.x / this.canvas.width * this.w;
                    this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][3] = mouseDelta.y / this.canvas.height * this.h;
                }

                // second - redraw bboxes

                this.drawBbox();
            }
            else {
                let pos = {
                    x : e.clientX - canvas.offsetLeft,
                    y : e.clientY - canvas.offsetTop,
                };
                let col = this.detectCollision(pos);
                if (col.x == 0 && col.y == 0) 
                {
                    canvas.style.cursor = 'crosshair';
                }
                else if (col.x != 0 && col.y == 0)
                {
                    canvas.style.cursor = 'e-resize';
                }
                else if (col.y != 0 && col.x == 0)
                {
                    canvas.style.cursor = 'n-resize';
                }
                else if (col.x * col.y > 0)
                {
                    canvas.style.cursor = 'se-resize';
                }
                else {
                    canvas.style.cursor = 'ne-resize';
                }

            }
        },

        processMouseUp(e) {
            if (this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][2] < 0) {
                this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][0] += this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][2];
                this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][2] *= -1;
            }
            if (this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][3] < 0) {
                this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][1] += this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][3];
                this.actions[this.videoName][this.resizedIdx].framesDict[this.currentFrame][3] *= -1;
            }

            this.ctx.fillStyle = '#fff';

            this.resizeMode = false;
            this.startPosition.x = null;
            this.startPosition.y = null;
        },

        drawBbox() {
            this.clear();
            this.transitionalBbox = {};

            for (let i = 0; i < this.bboxIdx.length; ++i) {
                this.ctx.beginPath();
                if (this.actions[this.videoName][this.bboxIdx[i]].framesDict.hasOwnProperty(this.currentFrame))
                {
                    var bbox = this.actions[this.videoName][this.bboxIdx[i]].framesDict[this.currentFrame];
                    this.ctx.rect(bbox[0] / this.w * this.canvas.width, bbox[1] / this.h * this.canvas.height, bbox[2] / this.w * this.canvas.width, bbox[3] / this.h * this.canvas.height);
                }
                else
                {
                    console.log('search neighbours');
                    let leftFrameNumber = this.findLeftClosestFrame(this.actions[this.videoName][this.bboxIdx[i]].framesDict, this.currentFrame);
                    let rightFrameNumber = this.findRightClosestFrame(this.actions[this.videoName][this.bboxIdx[i]].framesDict, this.currentFrame);

                    let leftBbox = this.actions[this.videoName][this.bboxIdx[i]].framesDict[leftFrameNumber];
                    let rightBbox = this.actions[this.videoName][this.bboxIdx[i]].framesDict[rightFrameNumber];

                    let coef = (this.currentFrame - leftFrameNumber) / (rightFrameNumber - leftFrameNumber);
                    Vue.set(this.transitionalBbox, this.bboxIdx[i], [
                        leftBbox[0] + (rightBbox[0] - leftBbox[0]) * coef,
                        leftBbox[1] + (rightBbox[1] - leftBbox[1]) * coef,
                        leftBbox[2] + (rightBbox[2] - leftBbox[2]) * coef,
                        leftBbox[3] + (rightBbox[3] - leftBbox[3]) * coef
                    ]);
                    this.ctx.rect(this.transitionalBbox[this.bboxIdx[i]][0] / this.w * this.canvas.width, 
                                  this.transitionalBbox[this.bboxIdx[i]][1] / this.h * this.canvas.height, 
                                  this.transitionalBbox[this.bboxIdx[i]][2] / this.w * this.canvas.width, 
                                  this.transitionalBbox[this.bboxIdx[i]][3] / this.h * this.canvas.height);
                }
                this.ctx.closePath();
                this.ctx.strokeStyle = '#f00';
                this.ctx.stroke();
            }
        },

        setBbox(bboxIdx, currentFrame) {
            this.bboxIdx = bboxIdx;
            this.currentFrame = currentFrame;
            this.drawBbox();
        },

        setVideoInfo(w, h, actions, videoName) {
            this.w = w;
            this.h = h;
            this.actions = actions;
            this.videoName = videoName;
        },

        clear() {
            this.ctx.clearRect(0, 0, canvas.width, canvas.height);
            this.ctx.beginPath();
            this.ctx.stroke();
        },

        detectCollision(pos) {
            let res = {x: 0, y: 0, idx: -1}; // 0 - no collision
            for (let i = 0; i < this.bboxIdx.length; ++i) {
                if (this.actions[this.videoName][this.bboxIdx[i]].framesDict.hasOwnProperty(this.currentFrame)) {
                    var bbox = this.actions[this.videoName][this.bboxIdx[i]].framesDict[this.currentFrame];
                }
                else {
                    var bbox = this.transitionalBbox[this.bboxIdx[i]];
                }

                if (pos.y - bbox[1] / this.h * this.canvas.height > -this.collisionEps && pos.y - (bbox[1] + bbox[3]) / this.h * this.canvas.height < this.collisionEps) {
                    if (Math.abs(bbox[0] / this.w * this.canvas.width - pos.x) < this.collisionEps) {
                        res.x = -1;
                    } else if (Math.abs((bbox[0] + bbox[2]) / this.w * this.canvas.width - pos.x) < this.collisionEps) {
                        res.x = 1;
                    }
                }

                if (pos.x - bbox[0] / this.w * this.canvas.width > -this.collisionEps && pos.x - (bbox[0] + bbox[2]) / this.w * this.canvas.width < this.collisionEps) {
                    if (Math.abs(bbox[1] / this.h * this.canvas.height - pos.y) < this.collisionEps) {
                        res.y = -1;
                    } else if (Math.abs((bbox[1] + bbox[3]) / this.h * this.canvas.height - pos.y) < this.collisionEps) {
                        res.y = 1;
                    }
                }

                if (res.x != 0 || res.y != 0) {
                    res.idx = this.bboxIdx[i];
                    return res;
                }
            }
            return res;
        },

        getNewActionID() {
            let maxID = 0;
            for (const vn in this.actions) {
                for (let i = 0; i < this.actions[vn].length; ++i) {
                    if (this.actions[vn][i].id > maxID) {
                        maxID = this.actions[vn][i].id;
                    }
                }
            }
            return maxID + 1;
        },

        findLeftClosestFrame(framesDict, frameNumber) {
            let res = -1;
            let minDelta = Number.MAX_SAFE_INTEGER;
            for (const n in framesDict) {
                if (n < frameNumber && frameNumber - n < minDelta) {
                    minDelta = frameNumber - n;
                    res = n;
                }
            }
            return res;
        },

        findRightClosestFrame(framesDict, frameNumber) {
            let res = -1;
            let minDelta = Number.MAX_SAFE_INTEGER;
            for (const n in framesDict) {
                if (n > frameNumber && n - frameNumber < minDelta) {
                    minDelta = n - frameNumber;
                    res = n;
                }
            }
            return res;
        }
    
    },
    mounted() {
        this.ctx = this.$refs.select.getContext('2d');
        this.canvas = this.$refs.select;
        this.canvas.height = 576;
        this.canvas.width = 1024;
        // this.ctx.fillRect(0,0,500,500);
    }
});

export default {
    components: {
        'video-player' : VideoPlayer,
        'alert' : Alert
    },

    data() {
        return {
            videoPlayer: '',
            currentDataset: 'VIRAT',
            currentVideoInfo: '',
            currentVideoPath: '',
            actions: [],
            videoInfo: [],
            manageForm: {
                idx: -1,
                type: '',
                start: 0,
                end: 0
            },
            desiredFrame: 0,
            alertMessage: '',
            alertVariant: 'success',
            showAlert: false
        };
    },

    methods: {
        getDataset() {
            const path = 'http://localhost:5000/actions';
            axios.get(path)
                .then((res) => {
                    this.actions = res.data.actions;
                    console.log(this.actions);
                    for (const videoName in this.actions) {
                        for (var i = 0; i < this.actions[videoName].length; ++i)
                        {
                            Vue.set(this.actions[videoName][i], 'selected', false);
                        }
                    }
                    
                    this.getVideoInfo();
                })
                .catch((error) => {
                    // eslint-отключение следующей строки
                });
        },
        getVideoInfo() {
            const path = 'http://localhost:5000/videos?dataset=' + this.currentDataset;
            axios.get(path)
                .then((res) => {
                    this.videoInfo = res.data.names;
                    this.updateVideo(this.videoInfo[0]);
                })
                .catch((error) => {
                    // eslint-отключение следующей строки
                });
        },
        saveDataset() {
            const path = 'http://localhost:5000/actions';
            let approvedActions = {};
            for (const videoName in this.actions) {
                Vue.set(approvedActions, videoName, []);
                for (const idx in this.actions[videoName]) {
                    if (this.actions[videoName][idx].approved) {
                        approvedActions[videoName].push(this.actions[videoName][idx]);
                    }
                }
            }
            axios.put(path, approvedActions)
                .then(
                    () => {
                        console.log('success');
                        this.alertMessage = 'Dataset successfully saved!';
                        this.alertVariant = 'success';
                        this.showAlert = true;
                        setTimeout(() => {this.showAlert = false}, 3000);
                    }
                )
                .catch(
                    (error) => {
                        this.alertMessage = 'Error occured!';
                        this.alertVariant = 'danger';
                        this.showAlert = true;
                        setTimeout(() => {this.showAlert = false}, 3000);
                    }
                );

        },
        onSubmit(evt) {
            evt.preventDefault();
            this.$refs.manageModal.hide();

            if (!this.actions[this.currentVideoInfo.name][this.manageForm.idx].framesDict.hasOwnProperty(this.manageForm.start)) {
                Vue.set(this.actions[this.currentVideoInfo.name][this.manageForm.idx].framesDict, 
                        this.manageForm.start, 
                        this.findBboxInClosestFrame(this.actions[this.currentVideoInfo.name][this.manageForm.idx].framesDict, this.manageForm.start).slice());
            }
            if (!this.actions[this.currentVideoInfo.name][this.manageForm.idx].framesDict.hasOwnProperty(this.manageForm.end)) {
                Vue.set(this.actions[this.currentVideoInfo.name][this.manageForm.idx].framesDict, 
                        this.manageForm.end, 
                        this.findBboxInClosestFrame(this.actions[this.currentVideoInfo.name][this.manageForm.idx].framesDict, this.manageForm.end).slice());
            }

            this.clipFramesDict(this.actions[this.currentVideoInfo.name][this.manageForm.idx].framesDict, this.manageForm.start, this.manageForm.end);
            console.log(this.actions[this.currentVideoInfo.name][this.manageForm.idx].framesDict);

            this.actions[this.currentVideoInfo.name][this.manageForm.idx].type = this.manageForm.type;
            this.actions[this.currentVideoInfo.name][this.manageForm.idx].start = this.manageForm.start;
            this.actions[this.currentVideoInfo.name][this.manageForm.idx].end = this.manageForm.end;

            this.updateVisibleBbox();
        },
        onReset(evt) {
            evt.preventDefault();
            this.$refs.manageModal.hide();

            this.actions[this.currentVideoInfo.name].splice(this.manageForm.idx, 1);

            this.updateVisibleBbox();
        },
        findBboxInClosestFrame(framesDict, frameNumber) {
            let res = -1;
            let minDelta = Number.MAX_SAFE_INTEGER;
            for (const n in framesDict) {
                if (Math.abs(n - frameNumber) < minDelta) {
                    minDelta = Math.abs(n - frameNumber);
                    res = n;
                }
            }
            return framesDict[res];
        },
        clipFramesDict(framesDict, start, end) {
            for (const n in framesDict) {
                if (n < start || n > end) {
                    delete framesDict.n;
                }
            }
        },
        updateVideo(video) {
            this.currentVideoInfo = video;
            if (!this.actions.hasOwnProperty(video.name)) {
                Vue.set(this.actions, video.name, []);
            }
            console.log(this.currentVideoInfo.name);
            this.$refs.draw.setVideoInfo(this.currentVideoInfo.w, this.currentVideoInfo.h, this.actions, this.currentVideoInfo.name);
            this.currentVideoPath = "http://localhost:5000/static/" + this.currentDataset + "/videos/" + this.currentVideoInfo.name + '.mp4';
        },
        updateAction(action, index) {
            this.manageForm.idx = index;
            this.manageForm.type = action.type;
            this.manageForm.start = action.start;
            this.manageForm.end = action.end;

        },
        seekToFrame() {
            console.log('seek');
            if (!this.videoPlayer.paused && !this.videoPlayer.ended) {
                this.videoPlayer.pause();
            }
            this.videoPlayer.currentTime = this.desiredFrame / this.currentVideoInfo.fps + 0.01;
        },
        updateVisibleBbox() {
            var currentFrame = Math.floor(this.videoPlayer.currentTime * this.currentVideoInfo.fps);
            this.desiredFrame = currentFrame;
            var currentFrameBboxIdx = []
            if (this.actions[this.currentVideoInfo.name]) {
                for(let i = 0; i < this.actions[this.currentVideoInfo.name].length; ++i) {
                    if (this.actions[this.currentVideoInfo.name][i].selected && 
                        this.actions[this.currentVideoInfo.name][i].start <= currentFrame && 
                        this.actions[this.currentVideoInfo.name][i].end >= currentFrame) {
                        currentFrameBboxIdx.push(i);
                    }
                }
            }
            this.$refs.draw.setBbox(currentFrameBboxIdx, currentFrame);
        },
        selectAll() {
            for(let i = 0; i < this.actions[this.currentVideoInfo.name].length; ++i) {
                this.actions[this.currentVideoInfo.name][i].selected = true;
            }
            this.updateVisibleBbox();            
        },
        deselectAll() {
            for(let i = 0; i < this.actions[this.currentVideoInfo.name].length; ++i) {
                this.actions[this.currentVideoInfo.name][i].selected = false;
            }
            this.updateVisibleBbox();            
        }
    },
    created() {
        this.getDataset();
    },
    mounted() {
        this.videoPlayer = document.getElementById('video-html-player');
        this.videoPlayer.addEventListener('timeupdate', (e) => {
            this.updateVisibleBbox();            
        });
    }
};
</script>

<style>
.row{
    width:650px; height:auto;
    position:absolute; top:10px; left:1204px;
    overflow: hidden;
}
.video-select{
    width:100px; height:576px;
    position:absolute; top:10px; left:10px;
}
.video-player-box{
    width:1024px; height:576px;
    position:absolute; top:10px; left:120px;
}
.labeling-box{
    width:1024px; height:576px;
    position:absolute; top:10px; left:120px;
    cursor: crosshair;
}
.frame-label{
    position:absolute; top:650px; left:120px;
}
.table-container{
    width: auto;
    max-height: 700px;
    overflow-x: visible;
    overflow-y: scroll;
}
</style>
