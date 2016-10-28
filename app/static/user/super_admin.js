// javascript file for super_admin
Vue.config.delimiters = ['${','}'];

$(document).ready(function(){
    var pathname = location.pathname;
    var path_arr = pathname.split("/");
    var path_item = path_arr[path_arr.length - 1];

    var _map = {
        'server_core' : ServerCorePage,
        'java_binary' : JavaBinary,
        'settings'    : Settings
    };

    // init
    new _map[path_item]();
});

function getCurrentHost(){
    var http = location.protocol;
    var slashes = http.concat("//");
    var host = slashes.concat(window.location.hostname);
    return host;
}

/*
* Server Core Page Management
* */
var ServerCorePage = function () {
    var self = this;
    this.upload_url = "/super_admin/upload_server_core";
    this._file_data = null;
    this.upload_vm = new Vue({
        el:"#upload_core",
        data:{
            allow_upload : true,
            file_name : "",
            mc_version : "",
            file_version : "",
            description : "",
            core_type : ""
        },
        computed:{
            allow_upload : function () {
                return !!(this.mc_version.length > 0 && this.file_name != "");
            }
        },
        methods:{
            "upload_file" : function () {
                self._file_data.formData = {
                    "mc_version" : self.upload_vm.mc_version,
                    "file_version" : self.upload_vm.file_version,
                    "description" : self.upload_vm.description,
                    "core_type" : self.upload_vm.core_type
                };

                self._file_data.submit().done(function (data) {
                    //TODO
                    console.log(data);
                    window.alert("Upload succeed!");
                });
            }
        }
    });
    
    this.__init__()
};

ServerCorePage.prototype.__init__ = function () {
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

var JavaBinary = function () {
    var self = this;

    var WAIT = 1,
        DOWNLOADING = 2,
        EXTRACTING = 3,
        FINISH = 4,
        FAIL = 5,
        EXTRACT_FAIL = 6;

    this.socket = io.connect(getCurrentHost()+":5001");
    this.socket.on("connect",function () {
       // self.socket.emit("message", pub_model);
    });
    self._init_download_list_listener(self.socket);

    this.flag_index_map = {};
    this.list_vm = new Vue({
        el:"#java_list",
        data:{
            "versions" : []
            /*status model :{
            *    "status" : WAIT,
            *    "progress" : 0.0
            * }
            * */
        },
        methods:{
            "dw_click" : function (index, event) {
                var btn_status = self.list_vm.versions[index].btn_status;
                
                switch(btn_status.status){
                    case FAIL:
                    case WAIT:
                        btn_status.status = DOWNLOADING;
                        var _major = self.list_vm.versions[index].major;
                        var _minor = self.list_vm.versions[index].minor;
                        self._start_downloading(_major, _minor, index);
                        self._add_socket_listener(self.socket, index);
                        break;
                    default:
                        break;
                }
            }
        }
    });

    self._init_list();
};

JavaBinary.prototype._generate_flag = function (num) {
    var series = "0123456789abcdefghijklmnopqrstuvwxyzZ";
    var str = "";
    for(var i=0;i<num;i++){
        str += series[Math.floor(Math.random() * 36)]
    }
    return str;
};
JavaBinary.prototype._init_list = function (callback) {
    var self = this;
    var socket = self.socket;
    var flag = self._generate_flag(16);

    var msg_json = {
        "event":"downloader.init_download_list",
        "flag" : flag,
        "props":{}
    };
    socket.emit("message", msg_json);
    /*
    $.get("/super_admin/java_binary/get_list", function (data) {
        try{
            var dt = JSON.parse(data);
            if(dt.status == "success"){

                callback(dt.info);
            }else{
                callback();
            }
        }catch(e){
            callback();
        }
    })*/
};

JavaBinary.prototype._start_downloading = function (major, minor, _index) {
    /*$.post("/super_admin/java_binary/download",{"major": major, "minor": minor}, function (data) {
        try{
            var dt = JSON.parse(data);
            if(dt.status == "success"){
                callback(dt.info);  // dt.info -> download hash
            }else{
                callback();
            }
        }catch(e){
            callback();
        }
    })*/
    var self = this;
    var socket = self.socket;
    var flag = self._generate_flag(16);
    var start_download_json = {
            "event":"downloader.add_download_java_task",
            "flag" : flag,
            "props": {
                "major": major,
                "minor" : minor
            }
        };

    self.flag_index_map[flag] = _index;
    socket.emit("message", start_download_json);
};

JavaBinary.prototype._init_download_list_listener = function (socket) {
    var self = this;
    var DOWNLOADING = 2;

    socket.on("message", function (msg) {
        console.log(msg);
        if(msg.event == "_init_download_list"){
            var data = msg.result;
            for(var item in data){
                var _status_model = {
                    "status":data[item]["dw"]["status"],
                    "progress" : data[item]["dw"]["progress"],
                    "_interval_flag" : 0
                };
                dw_hash = data[item]["dw"]["current_hash"];
                if(_status_model["progress"] == DOWNLOADING) {
                    _status_model._interval_flag = setInterval(function () {
                        var event_json = {
                            "event": "downloader.request_task_progress",
                            "flag": self._generate_flag(20),
                            "props": {
                                "hash": dw_hash
                            }
                        };
                        self.socket.emit("message", event_json);
                    }, 1000);
                }

                self.list_vm.versions.push({
                    "minor" : data[item].minor,
                    "major" : data[item].major,
                    "link"  : data[item].link,
                    "dw_hash" : dw_hash,
                    "btn_status" : _status_model
                });
            }
        }
    })
};

JavaBinary.prototype._add_socket_listener = function (socket) {
    var self = this;

    var WAIT = 1,
        DOWNLOADING = 2,
        EXTRACTING = 3,
        FINISH = 4,
        FAIL = 5,
        EXTRACT_FAIL = 6;

    function _find_index_by_hash(_hash){
        var list = self.list_vm.versions;
        for(var i=0;i<list.length;i++){
            if(list[i]["dw_hash"] == _hash){
                return i;
            }
        }
        return null;
    }

    socket.on("message", function (msg){

        msg["value"] = msg["result"];
        if(msg.event == "_get_progress") {
            _hash = msg["hash"];
            _total = msg["value"][1];
            _dw = msg["value"][0];

            _index = _find_index_by_hash(_hash);

            if (_total !== null && _dw !== null && _total > 0) {
                self.list_vm.versions[_index]["btn_status"]["progress"] = _dw / _total * 100;
            }
        }else if(msg.event == "_download_start"){
            dw_hash = msg["hash"];
            _index = self.flag_index_map[msg.flag];
            var btn_status = self.list_vm.versions[_index].btn_status;
            self.list_vm.versions[_index].dw_hash = dw_hash;

            if(dw_hash != null) {
                btn_status._interval_flag = setInterval(function () {
                    var event_json = {
                        "event": "downloader.request_task_progress",
                        "flag": self._generate_flag(20),
                        "props": {
                            "hash": dw_hash
                        }
                    };
                    self.socket.emit("message", event_json);
                }, 1000);
            }

        }else if(msg.event == "_download_finish"){
            _hash = msg["hash"];
            _result = msg["value"];

            _index = _find_index_by_hash(_hash);
            clearInterval(self.list_vm.versions[_index]["btn_status"]["_interval_flag"]);

            if(_result == true){
                self.list_vm.versions[_index]["btn_status"]["status"] = EXTRACTING;
            }else{
                self.list_vm.versions[_index]["btn_status"]["status"] = FAIL;
            }
        }else if(msg.event == "_extract_finish"){
            _hash = msg["hash"];
            _result = msg["value"];

            _index = _find_index_by_hash(_hash);
            clearInterval(self.list_vm.versions[_index]["btn_status"]["_interval_flag"]);
            if(_result == true){
                self.list_vm.versions[_index]["btn_status"]["status"] = FINISH; //extract success
            }else{
                self.list_vm.versions[_index]["btn_status"]["status"] = EXTRACT_FAIL;
            }
        }
    });
};

/*Settings*/
var Settings = function () {
    var self = this;

    this.set_passwd_vm = new Vue({
        el:"#password_settings",
        data:{
            ori_passwd : "",
            new_passwd : ""
        },
        methods:{
            'modify_passwd' : function () {
                self.set_password(self.set_passwd_vm.ori_passwd,
                self.set_passwd_vm.new_passwd, function () {
                    });
            }
        }
    });
};

Settings.prototype.set_password = function (ori_passwd, new_passwd, callback) {
    $.post("/super_admin/settings/passwd", {
        ori_password : ori_passwd,
        new_password : new_passwd
    }, function (data) {
        try{
            var dt = JSON.parse(data);
            console.log(dt);
            if(dt.status == "success"){
                callback(true);
            }
        }catch(e){
            callback(null);
        }
    })
};