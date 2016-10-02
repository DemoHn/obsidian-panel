// javascript file for super_admin
Vue.config.delimiters = ['${','}'];

$(document).ready(function(){
    var pathname = location.pathname;
    var path_arr = pathname.split("/");
    var path_item = path_arr[path_arr.length - 1];

    var _map = {
        'server_core' : ServerCorePage,
        'java_binary' : JavaBinary
    };

    // init
    new _map[path_item]();
});

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
        FAIL = 5;
    this.socket = io.connect("/dw");
    this.list_vm = new Vue({
        el:"#java_list",
        data:{
            "versions" : []
            /*status model :{
            *    "status" : WAIT,
            *    "progress" : 0.0,
            *    "is_extracting" : false
            * }
            * */
        },
        methods:{
            "dw_click" : function (index, event) {
                var btn_status = self.list_vm.versions[index].btn_status;
                
                switch(btn_status.status){
                    case WAIT:
                        btn_status.status = DOWNLOADING;
                        var _major = self.list_vm.versions[index].major;
                        var _minor = self.list_vm.versions[index].minor;
                        self._start_downloading(_major, _minor, function (dw_hash) {
                            if(dw_hash != null){
                                setInterval(function () {
                                    var event_json = {
                                        "hash" : dw_hash,
                                        "event" : "_request_progress",
                                        "value" : true
                                    };
                                    self.socket.emit("download_event", event_json);
                                },1000);
                            }
                        });

                        self._add_socket_listener(self.socket, index);
                        break;
                    default:
                        break;
                }
            }
        }
    });

    self._init_list(function (data) {
        if(data != null){
            // update data
            //add button status
            for(var item in data){
                var _status_model = {
                    "status":WAIT,
                    "progress" : 0.0,
                    "is_extracting" : false
                };

                self.list_vm.versions.push({
                    "minor" : data[item].minor,
                    "major" : data[item].major,
                    "link"  : data[item].link,
                    "btn_status" : _status_model
                });
            }
        }
    })
};

JavaBinary.prototype._init_list = function (callback) {
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
    })
};

JavaBinary.prototype._start_downloading = function (major, minor, callback) {
    $.post("/super_admin/java_binary/download",{"major": major, "minor": minor}, function (data) {
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
    })
};

JavaBinary.prototype._add_socket_listener = function (socket, index) {
    var self = this;
    socket.on("download_event", function (msg) {
        if(msg.event == "_get_progress"){
            _hash = msg["hash"];
            _total = msg["value"][1];
            _dw = msg["value"][0];

            if(_total !== null && _dw !== null && _total > 0){
                self.list_vm.versions[index]["btn_status"]["progress"] = _dw / _total * 100;
            }
        }else if(msg.event == "_download_finish"){

        }else if(msg.event == "_extract_finish"){
            // value is true or false
        }
    });
};