// Import System requirements
import Vue from 'vue';
import Resource from 'vue-resource';
import VueRouter from 'vue-router';

import routes_inst from './server_inst.routes';

// Import Views - Top level

import AppView from './views/App.vue';

// Resource logic
Vue.use(Resource);

Vue.use(VueRouter);

Vue.http.interceptors.push((request, next) => {
    /*
      Enable this when you have a backend that you authenticate against
      var headers = request.headers

      if (window.location.pathname !== '/login' && !headers.hasOwnProperty('Authorization')) {
      headers.Authorization = this.$store.state.token
      }
    */
    // console.log(headers)

    // continue to next interceptor without modifying the response
    next();
})

// Routing logic
var router = new VueRouter({
    routes: routes_inst,
    mode: 'history',
    scrollBehavior: function (to, from, savedPosition) {
        return savedPosition || { x: 0, y: 0 };
    }
});

// Some middleware to help us ensure the user is authenticated.
router.beforeEach((to, from, next) => {
    // window.console.log('Transition', transition)
    if (to.auth && (to.router.app.$store.state.token === 'null')) {
        window.console.log('Not authenticated');
        next({
            path: '/login',
            query: { redirect: to.fullPath }
        });
    } else {
        next();
    }
});

// Start out app!
// eslint-disable-next-line no-new
new Vue({
    el: '#root',
    router: router,
    render: h => h(AppView)
});
