// Import System requirements
import Vue from 'vue';
import Resource from 'vue-resource';

// Import Views - Top level

import StartupView from './views/startup/Main.vue';

// Import Install and register helper items
Vue.filter('count', count);
Vue.filter('domain', domain);
Vue.filter('prettyDate', prettyDate);
Vue.filter('pluralize', pluralize);

// Resource logic
Vue.use(Resource);

Vue.use(VueRouter);

Vue.http.interceptors.push((request, next) => {
    // continue to next interceptor without modifying the response
    next();
});

// Start out app!
// eslint-disable-next-line no-new
new Vue({
    el: '#root',
    render: h => h(StartupView)
});
