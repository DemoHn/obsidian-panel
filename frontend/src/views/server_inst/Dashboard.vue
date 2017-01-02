<template lang="html">
    <div>
        <div class="ctrl-bar">
            <inst-select ref="SelectF"></inst-select>
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
            </div>
        </div>
    </div>
</template>

<script>
    import SelectInstance from "../../components/dashboard/inst-select.vue";
    import ControlButton from "../../components/dashboard/ctrl-button.vue";
    import ServerStatus from "../../components/dashboard/server-status.vue";
    import SimpleConsole from "../../components/dashboard/simple-console.vue";

    import WebSocket from "../../lib/websocket";
    export default {
        components:{
            'inst-select' : SelectInstance,
            'ctrl-button' : ControlButton,
            'server-status' : ServerStatus,
            'simple-console': SimpleConsole
        },
        name: "Dashboard",
        data(){
            return {
                inst_id : null
            };
        },
        methods: {
            inst_cmd(command){
                let ws = new WebSocket();
                let props = {
                    inst_id : this.inst_id
                }

                if(command == "start"){
                    ws.send("process.start",props);
                }else if(command == "stop"){
                    ws.send("process.stop", props);
                }else if(command == "restart"){
                    ws.send("process.restart", props);
                }
            },

            send_command(command){
                let ws = new WebSocket();
                let Console = this.$refs.ConsoleF;
                if(Number.isInteger(this.inst_id)){
                    let props = {
                        "inst_id" : this.inst_id,
                        "command" : command
                    }
                    ws.send("process.send_command", props)
                }
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
            ws_init_console_log(){
                let ws = new WebSocket();
                let Console = this.$refs.ConsoleF;
                if(Number.isInteger(this.inst_id)){
                    let props = {
                        inst_id : this.inst_id
                    }
                    ws.send("process.get_instance_log", props, (msg)=>{
                        let log_obj = msg.val;
                        let log = log_obj["log"]
                        if(log != null){
                            Console.init_history_log(log.join(""));
                        }
                    });
                }
            },
            ws_init_status(){
                let ws = new WebSocket();
                let Status = this.$refs.StatusF;
                let Button = this.$refs.CtrlF;
                if(Number.isInteger(this.inst_id)){
                    let props = {
                        inst_id : this.inst_id
                    }
                    ws.send("process.get_instance_status", props, (msg)=>{
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
                    this.inst_id = msg.current_id;
                    this.ws_init_status();
                    this.ws_init_console_log();
                },(msg)=>{

                });

                ws.bind("status_change", this.on_status_change);
                ws.bind("player_change", this.on_player_change);
                ws.bind("memory_change", this.on_memory_change);
                ws.bind("log_update", this.on_log_update);

            }
        },
        mounted(){
            this.aj_get_list();
        }
    }
</script>

<style>
@media(min-width: 1201px){
    div.inst-content{
        position: relative;
        padding-left:250px;
        width:100%;
        z-index: 10;
        padding-top: 2rem;
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

@media(max-width: 767px){
    div.inst-content{
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 2rem;
    }
}
</style>
