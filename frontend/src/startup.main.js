// Import System requirements
var Vue = require('vue');
var VueMaterial = require('vue-material');

Vue.use(VueMaterial);
// Import Views - Top level

import StartupView from './views/startup/Main.vue';

window.paceOptions = {
    ajax: {
        trackWebSockets: false
    }
};

// Start out app!
// eslint-disable-next-line no-new
new Vue({
    el: '#root',
    render: h => h(StartupView)
});
