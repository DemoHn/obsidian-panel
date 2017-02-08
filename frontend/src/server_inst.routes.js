import LoginView from './views/Login.vue'
import NotFoundView from './views/404.vue'

// Import Views - Dash
import DashView from './views/server_inst/Dash.vue'
import EditInstanceView from './views/server_inst/EditInstance.vue'
import DashboardView from './views/server_inst/Dashboard.vue'
import NewInstanceView from './views/server_inst/NewInstance.vue'

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
            },
            {
                path: 'new_inst',
                component: NewInstanceView,
                name: "新的世界",
                description: "create new world"
            },
            {
                path: 'edit_inst/:id',
                component: EditInstanceView,
                name: "编辑",
                description: "edit pages"
            }
    ]
  }, {
    // not found handler
    path: '*',
    component: NotFoundView
  }
]

export default routes;
