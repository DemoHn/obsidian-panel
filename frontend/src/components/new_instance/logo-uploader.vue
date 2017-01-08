<template lang="html">
    <div>
        <span class="input-element">
            <span class="show-instance-logo">
                <div class="bottom-image" v-if="load_status === 0">
                    此处无图
                </div>
                <div class="bottom-image" v-if="load_status === 3">
                    上传错误
                </div>

                <div class="preview" v-else-if="load_status === 2">
                    <img :src="preview_target" alt="" class="preview_image"/>
                </div>

                <div class="loading" v-else-if="load_status === 1">
                    <i class="fa fa-spinner fa-pulse fa-2x fa-fw"></i>
                </div>
            </span>
            <span class="logo-ctrl">
                <div>
                    <vue-file-upload
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
    export default {
        name : "logo-uploader",
        components:{
            'vue-file-upload': VueFileUpload
        },
        data(){
            let v = this;
            return {
                load_status : NOT_LOAD,
                preview_target: "",
                file: null,
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
            _onCompeleteUpload(status, name){
                if(status){
                    let url = "/server_inst/preview_logo/" + name;
                    this.preview_target = url;
                    this.load_status = UPLOAD_SUCCESS;
                    this.$emit("upload_finish", url);
                }else{
                    this.load_status = UPLOAD_FAIL;
                }
            },
            _onErrorUpload(){
            },
            _onProgressUpload(progress){
                this.load_status = UPLOADING;
            }
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

</style>
