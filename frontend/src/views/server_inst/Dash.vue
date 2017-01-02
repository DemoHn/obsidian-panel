<template>
  <div class="wrapper">
    <header class="main-header">
      <a href="/" class="logo">
        <!-- LOGO -->
        <b>Obsidian</b> Panel
      </a>
      <!-- Header Navbar -->
      <nav class="navbar navbar-static-top" role="navigation">
        <a href="#" class="sidebar-toggle" role="button" data-toggle="offcanvas"><span class="sr-only"></span></a>

        <!-- Navbar Right Menu -->
        <div class="navbar-custom-menu">
            <ul class="nav navbar-nav">
                <li>
                    <a class="bottom" title="" id="_logout" data-placement="bottom" data-toggle="tooltip" href="/super_admin/logout" data-original-title="退出">
                        <i class="fa fa-power-off"></i>
                    </a>
                </li>
                <li><span>&nbsp;&nbsp;&nbsp;</span></li>
            </ul>
        </div>
      </nav>
    </header>
    <!-- Left side column. contains the logo and sidebar -->
    <aside class="main-sidebar">

      <!-- sidebar: style can be found in sidebar.less -->
      <section class="sidebar">
        <!-- Sidebar Menu -->
        <ul class="sidebar-menu">
          <li class="header"><i class="fa fa-map">&nbsp;&nbsp;我的世界</i></li>
          <li class="active pageLink" v-on:click="toggleMenu"><router-link to="/server_inst/dashboard"> <i class="fa fa-dashboard"></i> 仪表盘</router-link></li>

          <li class="header"><i class="fa fa-gear"></i>&nbsp;&nbsp;服务器设置</li>
          <li class="pageLink" v-on:click="toggleMenu"><router-link to="/super_admin/info"> <i class="fa fa-info-circle"></i> 基本信息</router-link></li>
        </ul>
        <!-- /.sidebar-menu -->
      </section>
      <!-- /.sidebar -->
    </aside>

    <!-- Content Wrapper. Contains page content -->
    <div class="content-wrapper">
      <router-view></router-view>
    </div>
    <!-- /.content-wrapper -->

    <!-- Main Footer -->
    <footer class="main-footer">
      <strong>Copyright &copy; {{year}} <a href="javascript:;">Obsidian Panel</a>.</strong> All rights reserved.
    </footer>
  </div>
  <!-- ./wrapper -->
</template>

<script>
import faker from 'faker'
import $ from 'jquery'

require('hideseek')

module.exports = {
  name: 'Dash',
  data: function () {
    return {
      section: 'Dash',
      me: '',
      error: '',
      api: {
        servers: {
          url: '', // Back end server
          result: []
        }
      }
    }
  },
  computed: {
    store: function () {
      return this.$parent.$store
    },
    state: function () {
      return this.store.state
    },
    callAPI: function () {
      return this.$parent.callAPI
    },
    demo: function () {
      return {
        displayName: faker.name.findName(),
        avatar: faker.image.avatar(),
        email: faker.internet.email(),
        randomCard: faker.helpers.createCard()
      }
    },
    year: function () {
      var y = new Date()
      return y.getFullYear()
    }
  },
  methods: {
    changeloading: function () {
      this.store.dispatch('TOGGLE_SEARCHING')
    },
    toggleMenu: function (event) {
      // remove active from li
      $('li.pageLink').removeClass('active')

      // Add it to the item that was clicked
      event.toElement.parentElement.className = 'pageLink active'
    }
  },
  mounted: function () {
  }
}
</script>

<style>
[v-cloak]{
  display: none;
}
.user-panel {
  height: 4em;
}
hr.visible-xs-block {
  width: 100%;
  background-color: rgba(0, 0, 0, 0.17);
  height: 1px;
  border-color: transparent;
}

@media(min-width: 1201px){
    div.content-wrapper{
        padding-left:15px;
        padding-right:15px;
        padding-top:18px;
    }
    div.box{
        max-width: 600px;
    }
}

/*Hide logo on mobile device*/
@media (max-width: 767px) {
    header.main-header a.logo{
        display: none;
    }

    .main-sidebar, .left-side{
        padding-top:50px !important;
    }
}
</style>
