// javascript file for super_admin
Vue.config.delimiters = ['${','}'];

$(document).ready(function(){
    var pathname = location.pathname;
    var path_arr = pathname.split("/");
    var path_item = path_arr[path_arr.length - 1];

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
    this.vm = new Vue({
        el:"#ttt",
        data:{
            "hello":"Hello"
        },
        computed:{

        },
        methods:{
            "cl":function () {
                $.get("/server_inst/boom",function (e) {
                    console.log(e)
                })
            }
        }
    });
    
  //  this.__init__()
};

Dashboard.prototype.__init__ = function () {
    var self = this;
    $("#file_select").fileupload({
        url : "/super_admin/upload_core_file",
        autoUpload: false,
        dataType : 'json'
    }).on('fileuploadadd', function (e,data) {
        self._file_data = data;

        self.upload_vm.file_name = data.files[0]['name'];
    });
};

var Console = function () {
    var self = this;
    // init
    var console_ta = document.getElementById("console");
    var editor = CodeMirror.fromTextArea(console_ta, {
        lineNumbers: true,
        readOnly : true
    });
    
    var socket = io.connect('/');
    socket.on("connect",function () {
        // on connect, server will emit an `ack` event

        socket.on("log_update",function (data) {
            _log = data["log"];
            editor.replaceRange(_log, CodeMirror.Pos(editor.lastLine()));
        });
    });

    $("#input").click(function () {
        socket.emit("command_input", {"command":$("#in").val()});
        console.log($("#in").val())
    })
};