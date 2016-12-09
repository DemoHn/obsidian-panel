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
    this.motd_editor = null;
    this.mobile_header_vm = new Vue({
        el:"#vue-steps",
        data:{
            index : 0
        }
    });

    this.logo_image_source = "";

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
            "range_players" : 1,
            "number_players" : 10,
            "range_RAM" : 1,
            "number_RAM" : 1,
            "data_port" : 0,
            "data_world_name" : "",
            "core_file_id" : "",
            "java_bin_id" : "",
            /*assert input*/
            "world_name_assert" : -1,
            "port_assert": -1,
            "ftp_account_assert" : -1,
            "basic_config_next_button" : false,
            "ftp_account_name" : FTP_ACCOUNT_NAME,
            "default_ftp_password" : true,

            /*server properties*/
            "server_properties" : "{}",
            "s_online_mode" : "true",
            "s_pvp" : "true",
            "s_difficulty" : 1,
            "s_spawn_monsters" : "true",
            "s_allow_nether" : "true",
            /*others*/
            "logo_url" : self.logo_image_source,
        },
       computed:{
            "number_RAM" : function (e) {
                return Math.pow(2, this.range_RAM)
            },
           "number_players" : function (e) {
               return this.range_players * 10
           },
           "basic_config_next_button": function (e) {
               return (this.world_name_assert == 1) && (this.port_assert == 1);
           },
           "server_properties": function (e) {
               return JSON.stringify({
                   "online-mode" : (this.s_online_mode === "true"),
                   "pvp" : (this.s_pvp === "true"),
                   "difficulty" : parseInt(this.s_difficulty),
                   "spawn-monsters" : (this.s_spawn_monsters === "true"),
                   "allow-nether" : (this.s_allow_nether === "true")
               })
           }
       },
       methods:{
           /*button click*/
           "next_to_2": function () {
               location.hash = "#conf_2";
           },
           "port_fs" : function () {
               this.port_assert = -1;
           },
           "port_bl" : function () {
               var that = this;
               if(this.data_port < 1 || this.data_port > 65535){
                   this.port_assert = 0;
               }else{
                   self.assert_data("port",this.data_port, function (data) {
                       if(data){
                           that.port_assert = 1;
                       }else{
                           that.port_assert = 0;
                       }
                   });
               }
           },
           "world_name_bl" : function () {
               var that = this;
               if(this.data_world_name == ""){
                   this.world_name_assert = 0;
               }else{
                   self.assert_data("inst_name",this.data_world_name, function (data) {
                       if(data){
                           that.world_name_assert = 1;
                       }else{
                           that.world_name_assert = 0;
                       }
                   });
               }
           },
           "world_name_fs" : function () {
               this.world_name_assert = -1;
           },
           "ftp_account_bl" : function () {
               var that = this;
               if(this.ftp_account_name == ""){
                   this.ftp_account_assert = 0;
               }else{
                   self.assert_data("ftp_account",this.ftp_account_name, function (data) {
                       if(data){
                           that.ftp_account_assert = 1;
                       }else{
                           that.ftp_account_assert = 0;
                       }
                   });
               }
           },
           "ftp_account_fs" : function () {
               this.ftp_account_assert = -1;         
           },
           "finish": function () {
               var that = this;

               $.post("/server_inst/new_inst", {
                   "inst_name" : that.data_world_name,
                   "core_file_id" : that.core_file_id,
                   "java_bin_id" : that.java_bin_id,
                   "listening_port" : that.data_port,
                   "max_RAM" : that.number_RAM,
                   "max_user" : that.number_players,
                   "server_properties" : that.server_properties,
                   "logo_url" : self.logo_image_source,
                   "motd" : self.parse_motd(),
                   "ftp_account" : that.ftp_account_name,
                   "ftp_default_password" : that.default_ftp_password,
                   "ftp_password" : that.ftp_password
               }, function (data) {
                   var d = JSON.parse(data);
                   if(d.status == "success"){
                       window.location.href = "/server_inst/dashboard/" + d.info;
                   }
               });
           }
       }
    });

    this.step_content_vm.$watch("index", function (newVal, oldVal) {
        if(newVal == 2){
            self.motd_editor = self.init_motd_editor();
            self.init_image_upload();
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

NewInstance.prototype.assert_data = function (type, data , callback) {
    $.get("/server_inst/new_inst/assert_input?type="+type+"&data="+data, function (data) {
        try{
            var d = JSON.parse(data);

            if(d.status == "success"){
                if(d.info == true){
                    callback(true);
                }else{
                    callback(false);
                }
            }else{
                callback(null);
            }
        }catch (e){
            callback(null);
        }
    })
};

/*we integrate a motd editor prototyped from ckeditor*/
NewInstance.prototype.init_motd_editor = function () {
    var motd_colors = [
        "#000000", "#0000be", "#00be00", "#00bebe", "#be0000",
        "#be00be", "#d9a334", "#bebebe", "#3f3f3f", "#3f3ffe",
        "#3ffe3f", "#3ffefe", "#fe3f3f", "#fe3ffe", "#fefe3f", "#ffffff"
    ];
    var toolbarOptions = [
        ['bold', 'italic', 'underline', 'strike'],
        [{ 'color': motd_colors }]
    ];
    var quill = new Quill("#motd-editor",{
        modules: {
            toolbar: toolbarOptions
        },
        placeholder: '苟利国家生死以...',
        theme: 'snow'
    });

    return quill;
};

NewInstance.prototype.init_image_upload = function () {
    var self = this;
    if(self.logo_image_source != ""){
        $("#preview_image").attr("src", "/server_inst/preview_logo/"+self.logo_image_source);
        $("#upload-mask").css("height", 0 + "px");
    }

    $("#upload_image").fileupload({
        url: "/server_inst/upload_logo",
        autoUpload: false,
        dataType: 'json',
        add: function (e, data) {
            // init mask
            $("#upload-mask").css("height", 64 + "px");

            if (data.files && data.files[0]) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    $('#preview_image').attr('src', e.target.result);
                };
                reader.readAsDataURL(data.files[0]);

                data.submit().success(function (result, textStatus, jqXHR) {
                    self.logo_image_source = result.info;
                });
            }
        },
        progressall: function (e, data) {
            var progress = data.loaded / data.total;
            $("#upload-mask").css("height", 64*(1-progress) + "px");
        }
    });
};

NewInstance.prototype.parse_motd = function () {
    var editor = this.motd_editor;
    var contents = editor.getContents().ops;

    var motd_colors = [
        "#000000", "#0000be", "#00be00", "#00bebe", "#be0000",
        "#be00be", "#d9a334", "#bebebe", "#3f3f3f", "#3f3ffe",
        "#3ffe3f", "#3ffefe", "#fe3f3f", "#fe3ffe", "#fefe3f", "#ffffff"
    ];
    /*
    * content format:
    * [
    *   {
    *      "insert" : ***,
    *      "attributes" : {
    *          <name> : <true | false>
    *      }
    *   }
    * ]
    *
    * And § (\u00A7) is Minecraft's color flag, which is necessary for
    * a colored text
    * */

    function utf8_encode(str){
        var f_str = "";
        for(var i=0;i<str.length;i++){
            num = str.charCodeAt(i);
            if(num > 0 && num < 128){
                f_str += str[i];
            }else{
                hex_code = num.toString(16);
                f_str += "\\u";
                for(var j=0;j<4-hex_code.length;j++){
                    f_str += "0"
                }

                f_str += hex_code;
            }
        }

        return f_str;
    }

    function SS(R){
        var ss = "\\u00a7" + R; //§
        return ss;
    }

    var parsed_string = "";
    var _count = 0;
    var attribute_table = [];

    // generate attribute table
    for(var i = 0;i < contents.length;i++){
        var attr_arr = [];
        if(contents[i].hasOwnProperty("attributes") == false){
            attr_arr.push("r");
        }else{
            var attr = contents[i]["attributes"];
            attr_arr.push("r");
            //color
            if(attr.hasOwnProperty("color")){
                for(var k = 0;k<motd_colors.length;k++){
                    if(attr["color"] == motd_colors[k]){
                        attr_arr.push(k.toString(16));
                        //parsed_string += SS(k.toString(16)) + utf8_encode(text);
                    }
                }
            }
            if(attr.hasOwnProperty("bold")){
                if(attr["bold"] === true){
                    attr_arr.push("l");
                }
            }
            if(attr.hasOwnProperty("strike")){
                if(attr["strike"] === true){
                    attr_arr.push("m");
                }
            }
            if(attr.hasOwnProperty("italic")){
                if(attr["italic"] === true){
                    attr_arr.push("o");
                }
            }
            if(attr.hasOwnProperty("underline")){
                if(attr["underline"] === true){
                    attr_arr.push("n");
                }
            }
        }
        attribute_table.push(attr_arr);
    }

    // then, use attribute table to parse string
    for(var k=0;k<attribute_table.length;k++){
        for(var l=0;l<attribute_table[k].length;l++){
            parsed_string += SS(attribute_table[k][l])
        }
        parsed_string += utf8_encode(contents[k]["insert"])
    }

    chop_arr = parsed_string.split("\n");

    if(chop_arr.length == 0){
        return "";
    }else if(chop_arr.length == 1){
        return chop_arr[0];
    }else{
        if(chop_arr[1].length > 0){
            return chop_arr[0] + "\n" + chop_arr[1];
        }else{
            return chop_arr[0];
        }
    }
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

            // and reset outer loop
            self.updateCircleLoop("online_player", 0);
            self.updateCircleLoop("RAM", 0);
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
    this.editor = this.init_embeded_console();
    this.fetch_status();

    $("#motd").html(self.encodeMOTD($("#motd").html()));
};

Dashboard.prototype.encodeMOTD = function(motd_string){

    function _format_style_string(char_code){
        var motd_colors = [
            "#000000", "#0000be", "#00be00", "#00bebe", "#be0000",
            "#be00be", "#d9a334", "#bebebe", "#3f3f3f", "#3f3ffe",
            "#3ffe3f", "#3ffefe", "#fe3f3f", "#fe3ffe", "#fefe3f", "#ffffff"
        ];

        if(/^[0-9a-fA-F]$/.test(char_code)){
            return "color : " + motd_colors[parseInt(char_code, 16)] + ";";
        }else if(char_code == "l"){
            return "font-weight: bold;";
        }else if(char_code == "m"){
            return "text-decoration: line-through;";
        }else if(char_code == "o"){
            return "font-style: italic;";
        }else if(char_code == "n"){
            return "text-decoration: underline;";
        }else{
            return "";
        }
    }
    
    // decode into utf-mode
    var motd_string = motd_string.replace(/\\u([0-9a-fA-F]{4})/g, function(match, p1){
        return String.fromCharCode(parseInt(p1, 16));
    });

    var motd_string = motd_string.trim();

    // then add format
    var format_table = motd_string.split("§r");

    var formatted_string = "";
    for(var i=0;i<format_table.length;i++){
        var _text = format_table[i];
        var f_arr = [];

        if(_text.length > 0){
            if(/§([0-9a-flmon])/gi.test(_text) == true){
                f_arr = /§([0-9a-flmon])/gi.exec(_text);
            }

            _text = _text.replace(/§([0-9a-flmon])/gi, "");
            for(var j=0;j<f_arr.length;j++){
                _text = "<span style='" + _format_style_string(f_arr[j]) + "'>" + _text + "</span>";
            }

            formatted_string += _text;
        }
    }
    return formatted_string;
}
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
            dvm.max_RAM = (data.total_RAM/1024);

        if(data.RAM != -1){
            dvm.current_RAM = (data.RAM/1024).toFixed(1);
            var ratio = data.RAM / data.total_RAM;
            dvm.RAM_percent = (ratio * 100).toFixed(0);
            self.updateCircleLoop("RAM", ratio);
        }
    }
};

Dashboard.prototype.init_embeded_console = function(callback){
    var self = this;
    var jq_input_cmd = $("#input_cmd");
    var jq_btn_enter = $("#btn_enter");

    function _send(){
        //avoid null input
        if(jq_input_cmd.val() == ""){
            return null;
        }
        var msg = {
            "event":"process.send_command",
            "flag" : self._generate_flag(16),
            "props":{
                "inst_id" : CURRENT_INSTANCE,
                "command" : jq_input_cmd.val()
            }
        };
        self.socket.emit("message", msg);
        // then clear input bar
        jq_input_cmd.val("");
    }
    // init input bar
    jq_input_cmd.on('keyup', function (e) {
        if(e.keyCode == 13){ // enter
            _send();
        }
    });

    jq_btn_enter.click(function(e){
        _send(); 
    });

    var editor = ace.edit("embeded-console");
    editor.$blockScrolling = Infinity;

    // set read only
    editor.setReadOnly(true);

    // set a light theme
    editor.setTheme("ace/theme/dawn");

    // not show line number
    editor.renderer.setOption('showLineNumbers', false);

    // set font size
    editor.setFontSize(12);
    editor.setShowPrintMargin(false);
    // wrap lines when a line is too long to show all
    editor.session.setOption('indentedSoftWrap', false);
    editor.session.setUseWrapMode(true);

    return editor;
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
        },400);
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

    if(type == "online_player"){
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
                var _ratio = (msg.value / dvm.total_player);
                self.updateCircleLoop("online_player", _ratio);
            }
        }else if(msg.event == "memory_change") {
            if(parseInt(self.inst_id) == parseInt(msg.inst_id)){
                dvm.current_RAM = (msg.value/1024).toFixed(2);
                ratio = ((msg.value/1024) / dvm.max_RAM);
                dvm.RAM_percent = (ratio*100).toFixed(0);
                self.updateCircleLoop("RAM", ratio);
            }
            //dvm.RAM_percent = msg.value /
        }else if(msg.event == "process.get_instance_status"){
            if(msg.status == "success"){
                self.updateDVM(msg.val);
            }
        }else if(msg.event == "log_update"){
            var _log = msg.value;
            var _inst_id = parseInt(msg.inst_id);

            if(self.inst_id == _inst_id){
                self.editor.session.insert({
                    row: self.editor.session.getLength(),
                    column: 0
                }, _log);

                // keep the cursor in the last line
                var row = self.editor.session.getLength();
                self.editor.gotoLine(row+1, 0);
            }
        }
    })
};

/* Console */
var Console = function () {
    var self = this;
    // init

    this.current_instance = CURRENT_INSTANCE;
    this.editor = this.init_console();

    var socket = io.connect(getCurrentHost()+":5001");

    var session = self.editor.session;
    socket.on("connect",function () {
        // on connect, server will emit an `ack` even

        socket.on("message",function (msg) {
            if(msg.event == "log_update") {
                _log = msg.value;
                session.insert({
                    row: session.getLength(),
                    column: 0
                }, _log);

                // keep the cursor in the last line
                var row = session.getLength();
                self.editor.gotoLine(row+1, 0);
            }
        });
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

    
    $("#input").click(function () {
        var msg = {
            "event":"process.send_command",
            "flag" : self._generate_flag(16),
            "props":{
                "inst_id" : CURRENT_INSTANCE,
                "command" : $("#in").val()
            }
        }
        socket.emit("message", msg);
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

Console.prototype.init_console = function () {
    //var console_ta = document.getElementById("console");
    /*    var editor = CodeMirror.fromTextArea(console_ta, {
        lineNumbers: true,
        readOnly : true
        });*/

    var editor = ace.edit("console");
    
    // just close the annoying hint
    editor.$blockScrolling = Infinity;

    // set read only
    editor.setReadOnly(true);
    return editor;
};
