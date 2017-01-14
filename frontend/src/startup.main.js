// Import System requirements
var Vue = require('vue');
var VueMaterial = require('vue-material');

Vue.use(VueMaterial);
// Import Views - Top level

import StartupView from './views/startup/Main.vue';

// Start out app!
// eslint-disable-next-line no-new
new Vue({
    el: '#root',
    render: h => h(StartupView)
});
