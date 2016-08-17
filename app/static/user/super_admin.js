// javascript file for super_admin
Vue.config.delimiters = ['${','}'];

$(document).ready(function(){
    var pathname = location.pathname;
    var path_arr = pathname.split("/");
    var path_item = path_arr[path_arr.length - 1];

    var _map = {
        'server_core' : ServerCorePage
    };

    // init
    _map[path_item]();
});

/*
* Server Core Page Management
* */
var ServerCorePage = function () {
    this.upload_url = "/super_admin/upload_server_core";
    this.upload_vm = new Vue({
        el:"#upload_core",
        data:{
            allow_upload : true,
            file_name : "",
            mc_version : "",
            file_version : "",
            description : ""
        },
        computed:{
            allow_upload : function () {
                return !!(this.mc_version.length > 0 && this.file_name != "");
            }
        },
        methods:{
            "upload_file" : function () {
                console.log(this.core_type)
            },
            "on_file_change" : function (e) {
                var files = e.target.files || e.dataTransfer.files;

                this.file_name = files[0]["name"];
            }
        }
    });
};

ServerCorePage.prototype._uploadFile = function (callback) {
    //$("#_upload_core_file").fileupload()
};