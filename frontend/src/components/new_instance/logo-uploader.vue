<template lang="html">
    <div class="main">
        <span class="input-element">
            <span class="show-instance-logo">
                <div class="bottom-image" v-if="load_status === 0">
                    此处无图
                </div>
                <div class="bottom-image" v-if="load_status === 3">
                    上传错误
                </div>

                <div class="preview" v-if="load_status === 2">
                    <img :src="preview_target" alt="" class="preview_image"/>
                </div>

                <div class="loading" v-if="load_status === 1">
                    <i class="fa fa-spinner fa-pulse fa-2x fa-fw"></i>
                </div>
            </span>
            <span class="logo-ctrl">
                <div>
                    <vue-file-upload v-if="!edit_mode"
                        ref="vueFileUploader"
                        name="file"
                        label="上传图片"
                        url="/server_inst/upload_logo"
                        :autoUpload = "auto_upload"
                        :filters = "filters"
                        :events = "cbEvents"
                        @onAdd="onAddItem"
                        >
                    </vue-file-upload>
                    <vue-file-upload v-if="edit_mode"
                        ref="vueFileUploader"
                        name="file"
                        label="上传图片"
                        :url="'/server_inst/edit_inst/' + inst_id + '/upload_logo'"
                        :autoUpload = "auto_upload"
                        :filters = "filters"
                        :events = "cbEvents"
                        @onAdd="onAddItem"
                        >
                    </vue-file-upload>

                    <button class="upload-like-btn" style="margin-left: 0.5rem;" v-if="has_img" @click="deleteImage">删除图片</button>
                </div>
                <div><span class="hint-text">注： 图片大小须为64*64像素，文件名以 .png 结尾</span></div>
            </span>
        </span>
    </div>
</template>

<script>
    const NOT_LOAD = 0;
    const UPLOADING = 1;
    const UPLOAD_SUCCESS = 2;
    const UPLOAD_FAIL = 3;
    import VueFileUpload from 'vue-file-upload';
    import WebSocket from "../../lib/websocket";

    let ws = new WebSocket();
    export default {
        name : "logo-uploader",
        components:{
            'vue-file-upload': VueFileUpload
        },
        props:{
            "inst_id" : {
                default : null,
            },
            "edit_mode":{
                default : false
            }
        },
        data(){
            let v = this;
            return {
                load_status : NOT_LOAD,
                preview_target: "",
                file: null,
                has_img: false,
                filters:[
                    {
                        name:"imageFilter",
                        fn(file){
                            var type = '|' + file.type.slice(file.type.lastIndexOf('/') + 1) + '|';
                            return '|jpg|png|jpeg|bmp|gif|'.indexOf(type) !== -1;
                        }
                    }
                ],
                cbEvents: {
                    onCompleteUpload(file,response,status,header){
                        let success = false;
                        if(status == 200 && response.code == 200){
                            success = true;
                        }
                        v._onCompeleteUpload(success, response.info);
                    },
                    onErrorUpload(file, response){
                        v._onErrorUpload();
                    },
                    onProgressUpload(file, progress){
                        v._onProgressUpload(progress);
                    }
                },
                _logo_image_source : "",
                auto_upload: true
            }
        },
        methods:{
            // $ref API
            getImageURL(){
                return this.preview_target;
            },

            onAddItem(files){
                this.file = files[files.length-1];
            },

            deleteImage(){
                let v = this;
                if(this.edit_mode){
                    ws.ajax("GET","/server_inst/edit_inst/" + this.inst_id + "/delete_logo", (msg)=>{
                        v.has_img = false;
                        v.load_status = NOT_LOAD;
                        v.preview_target = "";
                    })
                }else{
                    this.has_img = false;
                    this.preview_target = "";
                    this.load_status = NOT_LOAD;
                }
            },

            _detect_image(){
                let v = this;
                ws.ajax("GET", "/server_inst/edit_inst/" + this.inst_id + "/has_logo" , (msg)=>{
                    if(msg){
                        v.has_img = true;
                        v.load_status = UPLOAD_SUCCESS;
                        v.preview_target = "/server_inst/dashboard/logo_src/" + this.inst_id + "?random=" + new Date().getTime();
                    }else{
                        v.has_img = false;
                        v.load_status = NOT_LOAD;
                    }

                },(code)=>{

                })
            },
            _onCompeleteUpload(status, name){
                let _url = "";
                if(status){
                    if(this.edit_mode){
                        _url = "/server_inst/dashboard/logo_src/" + this.inst_id + "?random=" + new Date().getTime()
                    }else{
                        _url = "/server_inst/preview_logo/" + name;
                    }
                    this.has_img = true;
                    this.preview_target = _url;
                    this.load_status = UPLOAD_SUCCESS;
                    this.$emit("upload_finish", _url);
                }else{
                    this.load_status = UPLOAD_FAIL;
                }
            },
            _onErrorUpload(){
            },
            _onProgressUpload(progress){
                this.load_status = UPLOADING;
            }
        },
        mounted(){
            if(this.edit_mode)
                this._detect_image();
        }
    }
</script>

<style>
span.show-instance-logo{
    display: block;
    width:70px;
    height: 70px;
    padding:2px;
    border:1px solid #9f9f9f;
    border-radius: 2px;
    line-height: 68px;
    position: relative;
    float:left;
}

span.show-instance-logo img{
    width: 64px;
    height: 64px;
    display: block;
    position: absolute;
}

div.bottom-image{
    text-align: center;
    width: 64px;
    height: 64px;
    color: #aaaaaa;
    background-color: #f3f3f3;
    font-size: 12px;
    line-height: 64px;
    position: absolute;
}

div.upload-mask{
    position: absolute;
    width: 64px;
    height: 64px;
    background-color: rgba(255,255,255,0.6);
}

span.logo-ctrl{
    display: block;
    position:relative;
    width: 100%;
    padding-left: 90px;
}

span.hint-text{
    font-size: 12px;
    margin-top: 1em;
    display: inline-block;
    color: gray;
}

/*spinning button*/
div.preview{
    text-align: center;
    width: 64px;
    height: 64px;
    position: absolute;
}

div.preview img{
    position: relative;
    display: block;
    width: 64px;
    height: 64px;
}

div.loading{
    text-align: center;
    width: 64px;
    height: 64px;
    position: absolute;
    background-color: #fcfcfc;
    line-height: 64px;
}

div.loading i{
    line-height: 64px;
}

button.upload-like-btn{
    padding: 6px 12px;
    border:none;
    background-color: #d89704;
    line-height: 1.428573;
    font-size: 14px;
    color: white;
    vertical-align: middle;
}

div.main{
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
}
</style>
