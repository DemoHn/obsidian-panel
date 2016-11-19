// javascript file for super_admin
Vue.config.delimiters = ['${','}'];

$(document).ready(function(){
    var pathname = location.pathname;
    var path_arr = pathname.split("/");
    var path_item = path_arr[2];

    var _map = {
        'dashboard' : Dashboard,
        'console' : Console,
        'new_inst' : NewInstance
    };

    // init
    if(_map[path_item] != null){
        new _map[path_item]();
    }
});

function getCurrentHost(){
    var http = location.protocol;
    var slashes = http.concat("//");
    var host = slashes.concat(window.location.hostname);
    return host;
}
/*
* NewInstance page management
* */
var NewInstance = function () {
    var self = this;

    this.mobile_header_vm = new Vue({
        el:"#vue-steps",
        data:{
            index : 0
        }
    });

    this.header_vm = new Vue({
        el:"#vue-steps-desktop",
        data :{
            index : 0
        }
    });

   this.step_content_vm = new Vue({
        el:"#step-content",
        data :{
            index : 0,
            /*basic config vm*/
            "world_name" : "",
            "range_players" : 1,
            "number_players" : 10,
            "range_RAM" : 1,
            "number_RAM" : 1,
            "basic_config_next_button" : false
        },
       computed:{
            "number_RAM" : function (e) {
                return Math.pow(2, this.range_RAM)
            },
           "number_players" : function (e) {
               return this.range_players * 10
           }
        }
    });


    function hash_change() {
        var hash = location.hash;
        if(/([0-9]+)$/.test(hash) == true){
            var _index = /([0-9]+)$/.exec(hash);

            self.mobile_header_vm.index = parseInt(_index[0]) - 1;
            self.header_vm.index        = parseInt(_index[0]) - 1;
            self.step_content_vm.index  = parseInt(_index[0]) - 1;
        }else{
            self.mobile_header_vm._index = 0;
            self.header_vm.index = 0;
            self.step_content_vm.index = 0;
        }
    }

    $(window).on("hashchange", function () {
        hash_change();
    });

    hash_change();
};

/*
* Dashboard Page Management
* */
var Dashboard = function () {
    var self = this;
    
    this._file_data = null;
    // get instID rendered by template
    // of course if you fetch it from URL,
    // that's also fine
    /*CURRENT_INSTANCE is passed from template*/
    this.inst_id = CURRENT_INSTANCE;

    this.work_status = null;
    this.socket = io.connect(getCurrentHost()+":5001");

    this.dashboard_vm = new Vue({
        el:"#dash_board",
        data:{
            "work_status" : "-",
            "current_player" : "--",
            "total_player" : "--" ,
            "current_RAM" : "--",
            "max_RAM" : "--",
            "RAM_percent" : "--"
        }
    });

    this.select_menu_vm = new Vue({
        el:"#select_menu",
        data:{
            "markRotate": false,
            "dropdownExpand" : false
        },
        methods:{
            "menu_toggle": function (e) {
                this.markRotate = !this.markRotate;
                this.dropdownExpand = !this.dropdownExpand;
            }
        }
    });

    this.inst_ctrl_vm  = new Vue({
        "el":"#inst_ctrl",
        data: {
            "btn_status" : "start",
            "btn_disable" : true
        },
        methods:{
            "start_inst" : function (e) {
                self.inst_ctrl_vm.btn_disable = true;
                self.start_inst();
            },
            "stop_inst" : function (e) {
                self.inst_ctrl_vm.btn_disable = true;
                self.stop_inst();

            },
            "restart_inst" : function (e) {
                // TODO
                //self.restart_inst();
            }
        }
    });

    // watch changes and update something when work_status changed
    this.dashboard_vm.$watch('work_status', function (newVal, oldVal) {
        // update data
        self.work_status = newVal;
        self.UI_set_progress_animation(newVal);
        var dvm = self.dashboard_vm;
        // ctrl button status
        if(newVal == 0){
            self.inst_ctrl_vm.btn_disable = false;
            self.inst_ctrl_vm.btn_status = "start";
            dvm.current_player = "-";
            dvm.current_RAM = "-";
            dvm.RAM_percent = "--";
        } else if(newVal == 1){
            self.inst_ctrl_vm.btn_disable = true;
        }else if(newVal == 2){
            self.inst_ctrl_vm.btn_disable = false;
            self.inst_ctrl_vm.btn_status = "pause";
            dvm.current_player = 0;
        }


    });

    this._add_socket_listener(self.socket);
    //read status at the beginning
    this.fetch_status();
};

Dashboard.prototype.updateDVM = function (data) {

    var self = this;
    var dvm = self.dashboard_vm;
    if(data != null){
        dvm.work_status = data.status;
        if(data.current_player != -1){
            var ratio = data.current_player / data.total_player;
            dvm.current_player = data.current_player;
            self.updateCircleLoop("online_player", ratio);
        }

        if(data.total_player != -1)
            dvm.total_player = data.total_player;

        if(data.total_RAM != -1)
            dvm.max_RAM = data.total_RAM;

        if(data.RAM != -1){
            dvm.current_RAM = data.RAM.toFixed(1);
            var ratio = data.RAM / data.total_RAM;
            dvm.RAM_percent = (ratio * 100).toFixed(0);
            self.updateCircleLoop("RAM", ratio)
        }
    }
};

Dashboard.prototype.fetch_status = function (callback) {
    var self = this;
    /*$.post("/server_inst/dashboard/get_status",{"inst_id": self.inst_id}, function (data) {
        try{
            var dt = JSON.parse(data);
            if(dt.status == "success"){
                callback(dt.info);
            }
        }catch(e){
            callback(null);
        }
    })*/
    var get_instance_msg = {
        "event" : "process.get_instance_status",
        "flag" : self._generate_flag(32),
        "props":{
            "inst_id" : self.inst_id
        }
    };
    self.socket.emit("message", get_instance_msg);
    //callback(null);
};

Dashboard.prototype.UI_set_progress_animation = function (work_status) {
    var wa;
    var tr;
    function trig_rev() {
        setTimeout(function () {
            tr.play();
        },400)
    }
    function trig_wait() {
        tr.reset();
        wa.reset();
        wa.play();
    }

    switch (work_status){
        case 0:
            new Vivus('svg-halt', {duration: 30 , type:"sync"});
            break;
        case 1:
            wa = new Vivus('stop', {duration: 30 , type:"sync", start:"manual"}, trig_rev);
            tr = new Vivus('stop-rev', {duration: 30 , type:"sync", start:"manual"}, trig_wait);
            trig_wait();
            break;
        case 2:
            new Vivus('svg-running', {duration: 30 , type:"sync"});
            break;
    }

    new Vivus('online-users-svg', {duration: 50});
   // new Vivus('RAM-usage-svg', {duration: 30});
    //new Vivus('status-svg', {duration: 50}, myCallback);
};

Dashboard.prototype.updateCircleLoop = function (type, ratio) {
    function polarToCartesian(centerX, centerY, radius, angleInDegrees) {
      var angleInRadians = (angleInDegrees-90) * Math.PI / 180.0;

      return {
        x: centerX + (radius * Math.cos(angleInRadians)),
        y: centerY + (radius * Math.sin(angleInRadians))
      };
    }

    function describeArc(x, y, radius, startAngle, endAngle){

        var end = polarToCartesian(x, y, radius, endAngle);
        var start = polarToCartesian(x, y, radius, startAngle);

        var largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";

        var d = [
            "M", start.x, start.y,
            "A", radius, radius, 0, largeArcFlag, 1, end.x, end.y
        ].join(" ");

        return d;
    }

    if(type == 'online_player'){
        $("#online-users-svg path").attr("d", describeArc(100,100, 85, 0, 360*ratio));
    }else if(type == "RAM"){
        $("#RAM-usage-svg path").attr("d", describeArc(100,100, 85, 0, 360*ratio));
    }
};

Dashboard.prototype.start_inst = function () {
    var self = this;
    /*$.post("/server_inst/dashboard/start_inst",{"inst_id": self.inst_id}, function (data) {
        try{
            var dt = JSON.parse(data);
            if(dt.status == "success"){
                callback(dt.info);
            }
        }catch(e){
            callback(null);
        }
    })*/
    var start_instance_msg = {
        "event" : "process.start",
        "flag" : self._generate_flag(32),
        "props":{
            "inst_id" : self.inst_id
        }
    };
    self.socket.emit("message", start_instance_msg);
};

Dashboard.prototype.stop_inst = function () {
    var self = this;
    /*var self = this;
    $.post("/server_inst/dashboard/stop_inst",{"inst_id": self.inst_id}, function (data) {
        try{
            var dt = JSON.parse(data);
            if(dt.status == "success"){
                callback(dt.info);
            }
        }catch(e){
            callback(null);
        }
    })*/
    var stop_instance_msg = {
        "event" : "process.stop",
        "flag" : self._generate_flag(32),
        "props":{
            "inst_id" : self.inst_id
        }
    };
    self.socket.emit("message", stop_instance_msg);
};

Dashboard.prototype._generate_flag = function (num) {
    var series = "0123456789abcdefghijklmnopqrstuvwxyzZ";
    var str = "";
    for(var i=0;i<num;i++){
        str += series[Math.floor(Math.random() * 36)]
    }
    return str;
};

Dashboard.prototype._add_socket_listener = function (socket) {
    var self = this;
    var dvm  = self.dashboard_vm;
    socket.on("connect", function () {
        // enable start button
        self.dashboard_vm.start_btn_disable = false;
    });

    socket.on("message", function (msg) {
        if(msg.event == "status_change") {
            if(parseInt(self.inst_id) == parseInt(msg.inst_id)){
                // use watcher instead
                if (msg.value == 1) { // starting
                    dvm.work_status = 1;
                } else if (msg.value == 2) { //running
                    dvm.work_status = 2;
                } else { // msg.value == 0, halt
                    dvm.work_status = 0;
                }
            }
        }else if(msg.event == "player_change"){
            if(parseInt(self.inst_id) == parseInt(msg.inst_id)){
                dvm.current_player = msg.value;
                self.updateCircleLoop("online_player", ratio);
            }
        }else if(msg.event == "memory_change") {
            if(parseInt(self.inst_id) == parseInt(msg.inst_id)){
                dvm.current_RAM = msg.value.toFixed(1);
                ratio = (msg.value / dvm.max_RAM);
                dvm.RAM_percent = (ratio*100).toFixed(0);
                self.updateCircleLoop("RAM", ratio);
            }
            //dvm.RAM_percent = msg.value /
        }else if(msg.event == "process.get_instance_status"){
            if(msg.status == "success"){
                self.updateDVM(msg.val);
            }
            //console.log(msg);
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
    
    var socket = io.connect(getCurrentHost()+":5001");
    socket.on("connect",function () {
        // on connect, server will emit an `ack` even

        socket.on("message",function (msg) {
            if(msg.event == "log_update") {
                _log = msg.value;
                editor.replaceRange(_log, CodeMirror.Pos(editor.lastLine()));
            }
        });
    });

    $("#input").click(function () {
        var msg = {
            "event":"process.send_command",
            "flag" : self._generate_flag(16),
            "props":{
                "inst_id" : 1,
                "command" : $("#in").val()
            }
        }
        socket.emit("message", msg);
        //console.log($("#in").val())
    })
};

Console.prototype._generate_flag = function (num) {
    var series = "0123456789abcdefghijklmnopqrstuvwxyzZ";
    var str = "";
    for(var i=0;i<num;i++){
        str += series[Math.floor(Math.random() * 36)]
    }
    return str;
};