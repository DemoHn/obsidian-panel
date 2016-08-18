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
            description : ""
        },
        computed:{
            allow_upload : function () {
                return !!(this.mc_version.length > 0 && this.file_name != "");
            }
        },
        methods:{
            "upload_file" : function () {
                self._file_data.submit().done(function (data) {
                    //TODO
                    console.log(data);
                });
            }
        }
    });

    $("#file_select").fileupload({
        url : "/super_admin/upload_core_file",
        autoUpload: false,
        dataType : 'json'
    }).on('fileuploadadd', function (e,data) {
        self._file_data = data;

        self._file_data.formData = {
            "mc_version" : self.upload_vm.mc_version,
            "file_version" : self.upload_vm.file_version,
            "description" : self.upload_vm.description
        };
        self.upload_vm.file_name = data.files[0]['name'];
    });
    
};

ServerCorePage.prototype._uploadFile = function (callback) {

};