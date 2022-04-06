<template>
  <div class="labeling">
    <video-player class="video-player-box"></video-player>

    <div class="row">
      <div class="col-sm-10">
        <h1>Actions</h1>
        <hr><br><br>

        <button
         type="button"
         class="btn btn-success btn-sm"
         v-b-modal.action-modal>
          Add Action
        </button>

        <button
         type="button"
         class="btn btn-success btn-sm">
          Save
        </button>

        <br><br>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Class</th>
              <th scope="col">Start</th>
              <th scope="col">End</th>
              <th scope="col">Detect</th>
              <th scope="col">Track</th>
              <th scope="col">Class</th>
              <th></th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="(action, index) in actions" :key="index">
              <td>{{ action.type }}</td>
              <td>{{ action.start }}</td>
              <td>{{ action.end }}</td>
              <td>{{ action.detection_conf }}</td>
              <td>{{ action.tracking_conf }}</td>
              <td>{{ action.classification_conf }}</td>
              <td>
                <button v-if="action.approved"
                 type="button" class="btn btn-success btn-sm">Approved</button>
                <button v-else
                 type="button" class="btn btn-warning btn-sm">Approve</button>
                <button type="button" class="btn btn-danger btn-sm">Manage</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <b-modal ref="addActionModal"
         id="action-modal"
         title="Add new action"
         hide-footer>
      <b-form @submit="onSubmit" @reset="onReset" class="w-100">
        <b-form-group id="form-class-group"
                      label="Class:"
                      label-for="form-class-input">
          <b-form-input id="form-class-input"
                        type="text"
                        v-model="addActionForm.type"
                        required
                        placeholder="Enter class">
          </b-form-input>
        </b-form-group>

        <b-form-group id="form-time-group"
                      label="Time:"
                      label-for="form-time-input">
          <b-form-input id="form-start-input"
                        type="text"
                        v-model="addActionForm.start"
                        required
                        placeholder="Enter first frame time">
          </b-form-input>
          <b-form-input id="form-end-input"
                        type="text"
                        v-model="addActionForm.end"
                        required
                        placeholder="Enter last frame time">
          </b-form-input>
        </b-form-group>

        <b-button type="submit" variant="primary">Submit</b-button>
        <b-button type="reset" variant="danger">Reset</b-button>
      </b-form>
    </b-modal>
    <selection class="labeling-box"></selection>
  </div>
</template>

<script>
import axios from 'axios';
import Vue from 'vue';
import VideoPlayer from './VideoPlayer.vue'

Vue.component('selection', {
  template: "<canvas id='canvas' ref='select' @mousedown='startSelect' @mousemove='drawRect' @mouseup='stopSelect'></canvas>",
  data() {
    return {
      ctx: null,
      selectionMode: false,
      startPosition: {
        x: null,
        y: null,
      },
    };
  },

  methods: {

    startSelect(e) {
      this.selectionMode = true;
      this.startPosition.x = e.clientX - 10;
      this.startPosition.y = e.clientY - 10;
    },

    drawRect(e) {
      if (this.selectionMode) {
        this.ctx.beginPath();
        this.ctx.rect(
          this.startPosition.x,
          this.startPosition.y,
          e.clientX - 10 - this.startPosition.x,
          e.clientY - 10 - this.startPosition.y,
        );
        this.ctx.closePath();
        this.ctx.fillRect(0, 0, window.innerWidth, window.innerHeight);
        this.ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
        this.ctx.strokeStyle = '#f00';
        this.ctx.stroke();
      }
    },

    stopSelect(e) {
      this.ctx.fillStyle = '#fff';

      this.selectionMode = false;
      this.startPosition.x = null;
      this.startPosition.y = null;
    }
  
  },
  mounted() {
    this.$refs.select.height = 576;
    this.$refs.select.width = 1024;
    this.ctx = this.$refs.select.getContext('2d');
    // this.ctx.fillRect(0,0,500,500);
  }
});

export default {
  components: {
    'video-player' : VideoPlayer,
  },

  data() {
    return {
      actions: [],
      addActionForm: {
        type: '',
        start: '',
        end: ''
      },
    };
  },

  methods: {
    getActions() {
      const path = 'http://localhost:5000/actions';
      axios.get(path)
        .then((res) => {
          this.actions = res.data.actions;
        })
        .catch((error) => {
          // eslint-отключение следующей строки
        });
    },
    addAction(payload) {
      const path = 'http://localhost:5000/actions';
      axios.post(path, payload)
        .then(() => {
          this.getActions();
        })
        .catch((error) => {
          // eslint-отключение следующей строки
          this.getActions();
        });
    },
    initForm() {
      this.addActionForm.type = '';
      this.addActionForm.start = '0:00';
    },
    onSubmit(evt) {
      evt.preventDefault();
      this.$refs.addActionModal.hide();
      const payload = {
        type: this.addActionForm.type,
        start: this.addActionForm.start,
        end: this.addActionForm.end,
      };
      this.addAction(payload);
      this.initForm();
    },
    onReset(evt) {
      evt.preventDefault();
      this.$refs.addActionModal.hide();
      this.initForm();
    },
  },
  created() {
    this.getActions();
  },
};
</script>

<style>
.row{
  width:auto; height:auto;
  position:absolute; top:10px; left:1084px;
}
.video-player-box{
  width:1024px; height:576px;
  position:absolute; top:10px; left:10px;
}
.labeling-box{
  width:1024px; height:576px;
  position:absolute; top:10px; left:10px;
}
</style>
