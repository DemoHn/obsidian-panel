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

    this.dashboard_vm = new Vue({
        el:"#dash_board",
        data:{
            "work_status" : "-",
            "current_player" : "-",
            "total_player" : "-" ,
            "current_RAM" : "-", 
            "max_RAM" : "-",
            "start_btn" : true
        },
        computed:{

        },
        methods:{
        }
    });

    this.fetch_status(function (data) {
        var dvm = self.dashboard_vm;
        if(data != null){
            if(dvm.status != -1)
                switch(data.status){
                    case 0:
                        dvm.work_status = "未运行";
                        break;
                    case 1:
                        dvm.work_status = "启动中";
                        break;
                    case 2:
                        dvm.work_status = "运行中";
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


Dashboard.prototype._add_socket_listener = function (socket) {
    socket.on("inst_event", function (msg) {
        console.log(msg);
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

        socket.on("log_update",function (msg) {
            console.log(this);
            _log = msg["log"];
            editor.replaceRange(_log, CodeMirror.Pos(editor.lastLine()));
        });
    });

    $("#input").click(function () {
        socket.emit("command_input", {"command":$("#in").val()});
        //console.log($("#in").val())
    })
};