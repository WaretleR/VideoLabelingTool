import Vue from 'vue';
import Router from 'vue-router';
import Labeling from '@/components/Labeling';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'labeling',
      component: Labeling,
    },
  ],
  mode: 'history',
});
