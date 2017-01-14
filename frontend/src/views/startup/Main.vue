<template lang="html">
    <div class="bg-wrapper">
        <div class="box">
            <div class="logo"><b>Obsidian</b> Panel</div>
            <div class="box-content">
                <!--<register-user></register-user>-->
                <!--<set-database></set-database>-->
                <!--<user-login></user-login>-->
                <!--<port-settings></port-settings>-->
                <startup-finish></startup-finish>
            </div>
        </div>
    </div>
</template>

<script>
import WebSocket from "../../lib/websocket.js";
import RegisterUserView from "../../components/startup/register-user.vue";
import SetDatabaseView from "../../components/startup/set-database.vue";
import PortSettingsView from "../../components/startup/port-settings.vue";
import StartupFinishView from "../../components/startup/startup-finish.vue";
import UserLoginView from "../../components/startup/user-login.vue";

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

        }
    },

    methods :{

    },
    mounted(){
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
