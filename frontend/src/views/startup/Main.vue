<template lang="html">
    <div class="bg-wrapper">
        <div class="box">
            <div class="logo"><b>Obsidian</b> Panel</div>
            <div class="box-content">
                <user-login v-if="page_index == -1"></user-login>
                <register-user v-if="page_index == 1" @submit="user_submit"></register-user>
                <port-settings v-if="page_index == 2" @submit="port_submit"></port-settings>
                <set-database v-if="page_index == 3" @submit="db_submit"></set-database>
                <startup-finish v-if="page_index == 4"></startup-finish>
            </div>
        </div>

        <md-dialog-alert
            md-content="配置失败，请重新配置！"
            md-ok-text="确定"
            @close="onCloseErrorDialog"
            ref="error_dialog">
        </md-dialog-alert>
    </div>
</template>

<script>
import RegisterUserView from "../../components/startup/register-user.vue";
import SetDatabaseView from "../../components/startup/set-database.vue";
import PortSettingsView from "../../components/startup/port-settings.vue";
import StartupFinishView from "../../components/startup/startup-finish.vue";
import UserLoginView from "../../components/startup/user-login.vue";
import Vue from "vue";
import Resource from 'vue-resource';

Vue.use(Resource);

const LANG     = 0;
const REG_USER = 1;
const PORT_SET = 2;
const SET_DB   = 3;
const FINISH   = 4;
const LOGIN    = -1;

    let ajax = (method, url, data, on_success, on_fail) => {
        const ajax_info = {
            url: url,
            method: method,
            body: data
        };

        if(typeof(data) == "function"){
            on_fail    = on_success;
            on_success = data;
        }

        let vs = null;
        if(method == "GET"){
            vs = Vue.http.get(url);
        }else if(method == "POST"){
            vs = Vue.http.post(url, data);
        }
        vs.then((response)=>{
            try{
                let body = JSON.parse(response.body);
                if(body.status == "success"){
                    if(typeof(on_success) == "function"){
                        on_success(body["info"]);
                        return ;
                    }
                }else{
                    // not login
                    if(body.code == 403){
                        return ;
                    }
                    if(typeof(on_fail) == "function"){
                        on_fail(body["code"]);
                        return ;
                    }
                }
            }catch(e){
                if(typeof(on_fail) == "function"){
                    const error_code = 500;
                    on_fail(500);
                    return ;
                }
            }
        },(response)=>{
            if(typeof(on_fail) == "function"){
                on_fail(500);
                return ;
            }
        })
    }
export default {
    name: "main",
    components:{
        "register-user" : RegisterUserView,
        "set-database" : SetDatabaseView,
        "user-login" : UserLoginView,
        'port-settings' : PortSettingsView,
        "startup-finish" : StartupFinishView
    },
    data(){
        return {
            "page_index" : REG_USER,
            //lang
            "lang" : "",
            // root user
            "username" : "",
            "email" : "",
            "password" : "",
            // listen ports
            "app_port" : 80,
            "ftp_port" : 21,
            "msgQ_port" : 852,
            "ws_port" : 851,
            "pm_port" : 853,
            // database
            "db_env" : "sqlite",
            "mysql_username" : "",
            "mysql_password" : ""
        }
    },

    methods :{
        user_submit(data){
            this.email = data.email;
            this.username = data.username;
            this.password = data.password;
            // next page
            this.page_index = SET_DB;
        },
        db_submit(data){
            this.db_env = data.db_env;
            this.mysql_username = data.mysql_username;
            this.mysql_password = data.mysql_password;

            this.page_index = PORT_SET;
        },
        port_submit(data){
            this.app_port = data.app_port;
            this.ftp_port = data.ftp_port;
            this.msgQ_port = data.msgQ_port;
            this.ws_port = data.ws_port;
            this.pm_port = data.pm_port;

            let v = {
                "username" : this.username,
                "email" : this.email,
                "password" : this.password,
                "db_env" : this.db_env,
                "mysql_username" : this.mysql_username,
                "mysql_password" : this.mysql_password,
                "app_port" : this.app_port,
                "ftp_port" : this.ftp_port,
                "msgQ_port" : this.msgQ_port,
                "ws_port" : this.ws_port,
                "pm_port" : this.pm_port
            }

            ajax("POST","/startup/api/submit", v, this.submit_success, this.submit_fail)
        },
        submit_success(msg){
            this.page_index = FINISH;
        },
        submit_fail(code){
            if(code == 403){
                this.page_index = LOGIN;
            }else{
                this.$refs.error_dialog.open();
            }
        },
        onCloseErrorDialog(){
            this.page_index = REG_USER;
        }
    },
    mounted(){
        if(LOGIN_FLAG == 1){
            this.page_index = LOGIN;
        }else{
            //            this.page_index = LANG;
            this.page_index = REG_USER;
        }
    }

};
</script>

<style>
html, body{
    margin: 0;
    padding:0;
    height: 100%;
    width: 100%;
}

hr{
    margin-top: 1rem;
    border: 0;
    border-top: 1px solid #eee;
}

div.bg-wrapper{
    position: absolute;
    width: 100%;
    height: 100%;
    margin:0;
    padding: 0;
    background-color: #d2d6de;
}

div.logo{
    line-height: 1em !important;
    font-size: 35px;
    text-align: center;
    font-weight: 300;
    margin-bottom: 25px;
    color: #444;
}

div.box-content{
    background-color: #fff;
    padding: 20px;
    width: 100%;
    box-sizing: border-box;
}
@media(min-width:767px){
    div.box{
        width:400px;
        margin: 7% auto;
        box-sizing: border-box;
    }
}

@media(max-width:766px){
    div.box{
        width:90%;
        margin-top:20px;
        margin-left:auto;
        margin-right: auto;
    }
}
</style>
