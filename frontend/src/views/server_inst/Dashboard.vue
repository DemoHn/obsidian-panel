<template lang="html">
    <div>
        <div class="ctrl-bar">
            <inst-select ref="SelectF"
                         @click="toggle_inst"
                         :inst_id="inst_id"
                         ></inst-select>
            <ctrl-button ref="CtrlF"
                         @start_inst="inst_cmd('start')"
                         @stop_inst="inst_cmd('stop')"
                         @restart_inst="inst_cmd('restart')"
                         ></ctrl-button>
        </div>

        <div class="inst-content">
            <div class="row">
                <div class="col-md-7" id="dash_board">
                    <div class="box box-solid">
                        <div class="box-body">
                            <server-status ref="StatusF"></server-status>
                        </div>
                    </div>
                </div>
                <div class="col-md-5">
                    <div class="box box-solid">
                        <div class="box-body no-padding">
                            <table class="table table-striped inst-info-table">
                                <tbody>
                                    <tr>
                                        <td>LOGO</td>
                                        <td>
                                            <span id="show-instance-logo">
                                                <img :src="miscellaneous.image_source" alt="" id="preview_image" v-if="miscellaneous.image_soure != ''">
                                                <div id="bottom-image" v-else>
                                                    此处无图
                                                </div>
                                            </span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>每日讯息</td>
                                        <td>
                                            <span id="motd">
                                                <motd-display :content="miscellaneous.motd"></motd-display>
                                            </span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>IP / PORT</td>
                                        <td>{{ ip_port }}</td>
                                    </tr>
                                    <tr>
                                        <td>MC 版本</td>
                                        <td>{{miscellaneous.mc_version}}</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-7">
                    <div class="box box-solid">
                        <div class="box-body">
                            <simple-console
                                ref="ConsoleF"
                                @input="send_command"
                                ></simple-console>
                        </div>
                    </div>
                </div>
                <div class="col-md-5">
                    <div class="box box-solid">
                        <div class="box-body no-padding">
                            <table class="table table-striped inst-info-table">
                                <tbody>
                                    <tr>
                                        <td>FTP账户</td>
                                        <td>{{ miscellaneous.ftp_account_name }}</td>
                                    </tr>
                                    <tr>
                                        <td>FTP密码</td>
                                        <td style="color:gray;">
                                            <span v-if="miscellaneous.default_ftp_password === true">&lt; 与登录密码相同 &gt;</span>
                                            <span v-if="miscellaneous.default_ftp_password === false">&lt; 自定义密码 &gt;</span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                <div class="col-md-5">
                    <div class="box box-solid">
                        <div class="box-body no-padding">
                            <table class="table table-striped inst-info-table">
                                <tbody>
                                    <tr>
                                        <td>正版验证</td>
                                        <td>
                                            <span v-if="miscellaneous.server_properties['online-mode'] === 'true'">
                                                开启
                                            </span>
                                            <span v-else-if="miscellaneous.server_properties['online-mode'] === 'false'">
                                                关闭
                                            </span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>游戏难度</td>
                                        <td>{{ miscellaneous.server_properties['difficulty'] }}</td>
                                    </tr>
                                    <tr>
                                        <td>游戏模式</td>
                                        <td>{{ miscellaneous.server_properties['gamemode'] }}</td>
                                    </tr>
                                    <tr>
                                        <td>PVP</td>
                                        <td>
                                            <span v-if="miscellaneous.server_properties['pvp'] === 'true'">
                                                开启
                                            </span>
                                            <span v-else-if="miscellaneous.server_properties['pvp'] === 'false'">
                                                关闭
                                            </span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td>怪物生成</td>
                                            <td><span v-if="miscellaneous.server_properties['spawn-monsters'] === 'true'">
                                                开启
                                            </span>
                                            <span v-else-if="miscellaneous.server_properties['spawn-monsters'] === 'false'">
                                                关闭
                                            </span></td>
                                    </tr>
                                    <tr>
                                        <td>下界生成</td>
                                            <td><span v-if="miscellaneous.server_properties['allow-nether'] == 'true'">
                                                    开启
                                                </span>
                                                <span v-else-if="miscellaneous.server_properties['allow-nether'] == 'false'">
                                                    关闭
                                            </span></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import SelectInstance from "../../components/dashboard/inst-select.vue";
import ControlButton from "../../components/dashboard/ctrl-button.vue";
import ServerStatus from "../../components/dashboard/server-status.vue";
import SimpleConsole from "../../components/dashboard/simple-console.vue";
import MotdDisplay from "../../components/dashboard/motd-display.vue";

import WebSocket from "../../lib/websocket";
export default {
    components:{
        'inst-select' : SelectInstance,
        'ctrl-button' : ControlButton,
        'server-status' : ServerStatus,
        'simple-console': SimpleConsole,
        'motd-display' : MotdDisplay
    },
    name: "Dashboard",
    data(){
        return {
            inst_id : null,
            miscellaneous: {
                motd : "",
                mc_version : "",
                image_source : "",
                ftp_account_name : "",
                default_ftp_password: "",
                server_properties: {},
                listen_port : null,
            },
            ip_addr: null,
            ip_port: null
        };
    },
    computed: {
        ip_port(){
            if(this.miscellaneous.listen_port == null){
                return '';
            }else if(this.ip_addr == null){
                return "*:"+ this.miscellaneous.listen_port;
            }else{
                return this.ip_addr + ":" + this.miscellaneous.listen_port;
            }
        }
    },
    methods: {
        inst_cmd(command){
            let ws = new WebSocket();

            if(command == "start"){
                ws.ajax("GET", "/server_inst/api/start_instance/"+this.inst_id, (msg)=>{});
            }else if(command == "stop"){
                ws.ajax("GET", "/server_inst/api/stop_instance/"+this.inst_id, (msg)=>{});
            }else if(command == "restart"){
                ws.ajax("GET", "/server_inst/api/restart_instance/"+this.inst_id, (msg)=>{});
            }
        },

        send_command(command){
            let ws = new WebSocket();
            let Console = this.$refs.ConsoleF;
            if(Number.isInteger(this.inst_id)){
                ws.ajax("GET","/server_inst/api/send_command/"+this.inst_id + "?" + "command=" + command);
            }
        },

        toggle_inst(inst_id){
            // toggle inst_id
            this.inst_id = inst_id;
            let Status = this.$refs.StatusF;

            Status.set_loading_status(true);
            this.aj_get_properties();
            this.aj_init_status();
            this.aj_init_console_log();
        },
        // events originally from MPW
        on_status_change(msg){
            if(msg.inst_id == this.inst_id){
                let Status = this.$refs.StatusF;
                let Button = this.$refs.CtrlF;
                let work_status = msg.value;
                // operation
                Status.set_status(work_status);
                Button.init(work_status);
            }
        },

        on_player_change(msg){
            if(msg.inst_id == this.inst_id){
                let Status = this.$refs.StatusF;
                let Button = this.$refs.CtrlF;

                let online_player = msg.value;
                Status.set_online_player(online_player);
            }
        },

        on_memory_change(msg){
            if(msg.inst_id == this.inst_id){
                let Status = this.$refs.StatusF;
                let Button = this.$refs.CtrlF;

                let RAM = msg.value;
                Status.set_RAM(RAM);
            }
        },

        on_log_update(msg){
            var _log = msg.value;
            let Console = this.$refs.ConsoleF;
            if(this.inst_id == parseInt(msg.inst_id)){
                Console.append_log(_log);
            }
        },
        aj_init_console_log(){
            let ws = new WebSocket();
            let Console = this.$refs.ConsoleF;
            if(Number.isInteger(this.inst_id)){
                ws.ajax("GET", "/server_inst/api/get_instance_log/"+this.inst_id, (msg)=>{
                    let log_obj = msg.val;
                    let log = log_obj["log"]
                    if(log != null){
                        Console.init_history_log(log.join(""));
                    }
                });
            }
        },
        aj_init_status(){
            let ws = new WebSocket();
            let Status = this.$refs.StatusF;
            let Button = this.$refs.CtrlF;
            if(Number.isInteger(this.inst_id)){
                let props = {
                    inst_id : this.inst_id
                }
                ws.ajax("GET", "/server_inst/api/get_instance_status/"+this.inst_id, (msg)=>{
                    Status.init_status_list(msg.val);
                    Button.init(msg.val.status);
                });
            }
        },
        aj_get_list(){
            let Select = this.$refs.SelectF;
            let ws = new WebSocket();
            ws.ajax("GET","/server_inst/api/get_inst_list", (msg)=>{
                Select.init_inst_list(msg);

                if(this.inst_id == null)
                    this.inst_id = msg.current_id;

                this.aj_get_properties();
                this.aj_init_status();
                this.aj_init_console_log();
            },(msg)=>{

            })
            ws.bind("status_change", this.on_status_change);
            ws.bind("player_change", this.on_player_change);
            ws.bind("memory_change", this.on_memory_change);
            ws.bind("log_update", this.on_log_update);
        },
        aj_get_properties(){
            let ws = new WebSocket();
            let inst_id = this.inst_id;
            ws.ajax("GET","/server_inst/api/get_miscellaneous_info/"+inst_id, (msg)=>{
                for(let key in msg){
                    this.miscellaneous[key] = msg[key];
                }
            },(msg)=>{
                // on error
            })
        },
        aj_get_ip_address(){
            let ws = new WebSocket();
            ws.ajax("GET","/server_inst/api/get_my_ip", (msg)=>{
                this.ip_addr = msg;
            },(msg)=>{
                // on error
            })
        }
    },
    mounted(){
        // init with hash
        let hash = window.location.hash;
        if(hash !== ""){
            try{
                this.inst_id = parseInt(hash.substr(1));
            }catch(e){
                this.inst_id = null;
            }
        }
        this.aj_get_list();
        this.aj_get_ip_address();
    }
}
    </script>

<style>
    @media(min-width: 1201px){
        div.inst-content{
            position: absolute;
            padding-left:250px;
            width:100%;
            z-index: 10;
            padding-top: 2rem;
            max-width: 1350px;
        }

        div.ctrl-bar{
            width : 220px;
            position: relative;
            float: left;
            margin-top: 2rem;
            padding-left: 10px;
            padding-right: 10px;
            z-index: 12;
        }
    }

    @media(max-width: 1201px){
        div.inst-content{
            padding-left: 1.5rem;
            padding-right: 1.5rem;
            padding-top: 2rem;
        }
    }

    /*instance info (general and game-specific) table style*/
table.inst-info-table tr td{
    padding-right: 1.5rem;
    vertical-align: middle;
    box-sizing: border-box;
}

table.inst-info-table tr td:nth-child(1),
table.inst-info-table tr td:nth-child(3)
{
    text-align: right;
    font-weight: bold;
    width: 15%;
}


table.inst-info-table tr td:nth-child(2),
table.inst-info-table tr td:nth-child(4)
{
    width: 35%;
}

span#show-instance-logo{
    display: inline-block;
    width:70px;
    height: 70px;
    padding:2px;
    border:1px solid #9f9f9f;
    border-radius: 2px;
    line-height: 68px;
}

span#show-instance-logo img{
    width: 64px;
    height: 64px;
    display: block;
    position: absolute;
}

div#bottom-image{
    text-align: center;
    width: 64px;
    height: 64px;
    color: #aaaaaa;
    background-color: #f3f3f3;
    font-size: 12px;
    line-height: 64px;
    position: absolute;
}

span#motd{
    display: inline-block;
    max-width: 20rem;
}

</style>
