import LoginView from './views/Login.vue'
import NotFoundView from './views/404.vue'

// Import Views - Dash
import DashView from './views/super_admin/Dash.vue'
import JavaBinaryView from './views/super_admin/JavaBinary.vue'
import SettingsView from './views/super_admin/Settings.vue'
import ServerCoreView from './views/super_admin/ServerCore.vue'
import InfoView from './views/super_admin/Info.vue'

// Routes
const routes = [
    {
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
