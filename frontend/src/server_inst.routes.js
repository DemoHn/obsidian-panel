import LoginView from './views/Login.vue'
import NotFoundView from './views/404.vue'

// Import Views - Dash
import DashView from './views/server_inst/Dash.vue'
import DashboardView from './views/server_inst/Dashboard.vue'


// Routes
const routes = [
    {
        path: '/server_inst/',
        component: DashView,
        auth: false,
        children: [
      {
          path: 'dashboard',
          component: DashboardView,
          name: '控制台',
          description: 'Overview of environment'
      }
    ]
  }, {
    // not found handler
    path: '*',
    component: NotFoundView
  }
]

export default routes;
