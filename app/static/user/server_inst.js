// javascript file for super_admin
Vue.config.delimiters = ['${','}'];

$(document).ready(function(){
    var pathname = location.pathname;
    var path_arr = pathname.split("/");
    var path_item = path_arr[2];

    var _map = {
        'dashboard' : Dashboard,
        'console' : Console
    };

    // init
    new _map[path_item]();
});

/*
* Server Core Page Management
* */
var Dashboard = function () {
    var self = this;
    
    this._file_data = null;
    // get instID rendered by template
    // of course if you fetch it from URL,
    // that's also fine
    this.inst_id = $("#instID").val();
    this.socket = io.connect("/channel_inst");

    this.status_dict = {
        "0" : "未运行",
        "1" : "启动中",
        "2" : "运行中"
    };

    this.dashboard_vm = new Vue({
        el:"#dash_board",
        data:{
            "work_status" : "-",
            "current_player" : "-",
            "total_player" : "-" ,
            "current_RAM" : "-", 
            "max_RAM" : "-",
            "start_btn" : true,
            "start_btn_disable" : true,
            "stop_btn_disable" : true
        },
        computed:{

        },
        methods:{
            "start_inst" : function (e) {
                self.start_inst(function (i_id) {/* nothing */ })
            },
            "stop_inst" : function (e) {
                self.stop_inst(function (i_id) {/* nothing */ })
            }
        }
    });

    this._add_socket_listener(self.socket);
    //read status at the beginning
    this.fetch_status(function (data) {
        var dvm = self.dashboard_vm;
        if(data != null){
            if(dvm.status != -1)
                switch(data.status){
                    case 0:
                        dvm.work_status = self.status_dict["0"];
                        dvm.start_btn = true;
                        dvm.start_btn_disable = false;
                        break;
                    case 1:
                        dvm.work_status = self.status_dict["1"];
                        //dvm.work_status = "启动中";
                        dvm.start_btn = false;
                        dvm.stop_btn_disable = true;
                        break;
                    case 2:
                        dvm.work_status = self.status_dict["2"];
                        //dvm.work_status = "运行中";
                        dvm.start_btn = false;
                        dvm.stop_btn_disable = false;
                        break;
                    default:
                        break;
                }


            if(data.current_player != -1)
                dvm.current_player = data.current_player;

            if(data.max_player != -1)
                dvm.total_player = data.max_player;

            if(data.max_RAM != -1)
                dvm.max_RAM = data.max_RAM;

            if(data.current_RAM != -1)
                dvm.current_RAM = data.current_RAM;
        }
    });
};

Dashboard.prototype.fetch_status = function (callback) {
    var self = this;
    $.post("/server_inst/dashboard/get_status",{"inst_id": self.inst_id}, function (data) {
        try{
            var dt = JSON.parse(data);
            if(dt.status == "success"){
                callback(dt.info);
            }
        }catch(e){
            callback(null);
        }
    })
};

Dashboard.prototype.start_inst = function (callback) {
    var self = this;
    $.post("/server_inst/dashboard/start_inst",{"inst_id": self.inst_id}, function (data) {
        try{
            var dt = JSON.parse(data);
            if(dt.status == "success"){
                callback(dt.info);
            }
        }catch(e){
            callback(null);
        }
    })
};

Dashboard.prototype.stop_inst = function (callback) {
    var self = this;
    $.post("/server_inst/dashboard/stop_inst",{"inst_id": self.inst_id}, function (data) {
        try{
            var dt = JSON.parse(data);
            if(dt.status == "success"){
                callback(dt.info);
            }
        }catch(e){
            callback(null);
        }
    })
};

Dashboard.prototype._add_socket_listener = function (socket) {
    var self = this;
    var dvm  = self.dashboard_vm;
    socket.on("connect", function () {
        // enable the button
        self.dashboard_vm.start_btn_disable = false;
    });

    socket.on("inst_event", function (msg) {
        if(msg.event == "status_change"){

            if(msg.value == 1){ // starting
                dvm.work_status = self.status_dict["1"];
                dvm.start_btn = false;
                dvm.stop_btn_disable = true;

            }else if(msg.value == 2){ //running
                dvm.work_status = self.status_dict["2"];
                dvm.start_btn = false;
                dvm.stop_btn_disable = false;
                dvm.current_player = 0;
            }else{ // msg.value == 0, halt
                dvm.work_status = self.status_dict["0"];

            }
        }else if(msg.event == "player_change"){
            dvm.current_player = msg.value;
        }else if(msg.event == "memory_change") {
            dvm.current_RAM = msg.value.toFixed(1);
        }
    })
};

/* Console */
var Console = function () {
    var self = this;
    // init
    var console_ta = document.getElementById("console");
    var editor = CodeMirror.fromTextArea(console_ta, {
        lineNumbers: true,
        readOnly : true
    });
    
    var socket = io.connect('/channel_inst');
    socket.on("connect",function () {
        // on connect, server will emit an `ack` event
        console.log("id: "+socket.id);

        socket.on("inst_event",function (msg) {
            if(msg.event = "log_update")
            _log = msg.value;
            editor.replaceRange(_log, CodeMirror.Pos(editor.lastLine()));
        });
    });

    $("#input").click(function () {
        socket.emit("command_input", {"command":$("#in").val()});
        //console.log($("#in").val())
    })
};