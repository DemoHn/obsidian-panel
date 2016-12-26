import DashView from './components/Dash.vue'
import LoginView from './components/Login.vue'
import NotFoundView from './components/404.vue'

// Import Views - Dash
import DashboardView from './components/dash/Dashboard.vue'
import JavaBinaryView from './views/JavaBinary.vue'
import SettingsView from './views/Settings.vue'
import ServerCoreView from './views/ServerCore.vue'
import InfoView from './views/Info.vue'

// Routes
const routes = [
/*  {
    path: '/login',
    component: LoginView
  },*/ {
    path: '/super_admin/',
    component: DashView,
    auth: false,
    children: [
      {
        path: 'java_binary',
        component: JavaBinaryView,
        name: 'Java版本管理',
        description: 'Overview of environment'
      }, {
        path: 'info',
        component: InfoView,
        name: 'INFO',
        description: 'Simple and advance table in CoPilot'
      }, {
        path: 'server_core',
        component: ServerCoreView,
        name: 'Server CORE',
        description: 'Tasks page in the form of a timeline'
      }, {
        path: 'settings',
        component: SettingsView,
        name: 'Settings',
        description: 'User settings page'
      }
    ]
  }, {
    // not found handler
    path: '*',
    component: NotFoundView
  }
]

export default routes;
