<template lang="html">
    <div class="edit_model_content">
        <div class="form_group">
            <div class="form_label">
                文件名：
            </div>
            <div class="form_input">
                <input type="text" class="form-control input-file-name" readonly v-model="file_name"/>
                <vue-file-upload
                    ref="vueFileUploader"
                    url="/super_admin/api/upload_core_file"
                    name="files"
                    label="选择文件"
                    :filters = "filters"
                    :events = 'cbEvents'
                    :request-options = "reqopts"
                    @onAdd = "onAddItem"
                    ></vue-file-upload>
            </div>
        </div>
        <div class="form_group">
            <div class="form_label">
                类型：
            </div>
            <div class="form_input">
                <select name="" class="form-control" v-model="core_type">
                    <option :value="'bukkit'">Bukkit</option>
                    <option :value="'spigot'">Spigot</option>
                    <option :value="'vanilla'">Vanilla</option>
                    <option :value="'forge'">Forge</option>
                    <option :value="'mcpc'">MCPC+</option>
                    <option :value="'kcauldron'">KCauldron</option>
                    <option :value="'thermos'">Thermos</option>
                    <option :value="'torch'">Torch</option>
                    <option :value="'other'">其他</option>
                </select>
            </div>
        </div>
        <div class="form_group">
            <div class="form_label">MC版本：&nbsp;<i class="red-multiple"></i></div>
            <div class="form_input">
                <input type="text" class="form-control" v-model="minecraft_version" placeholder="此核心对应的MC客户端版本"/>
            </div>
        </div>
        <div class="form_group">
            <div class="form_label">
                文件版本：
            </div>
            <div class="form_input">
                <input type="text" class="form-control" v-model="core_version" placeholder="核心文件的版本"/>
            </div>
        </div>
        <div class="form_group">
            <div class="form_label">
                备注：
            </div>
            <div class="form_input">
                <textarea class="form-control" v-model="note" placeholder="对这个核心的特别说明"></textarea>
            </div>
        </div>
        <progress-bar :progress="progress_bar_ratio"
                      label_uploading="正在上传"
                      label_success="上传成功"
                      label_fail="上传失败"
                      :status="progress_bar_status"
                      v-if="show_progress_bar"></progress-bar>
        <!-- upload progress-->
        <!--<transition name="dropdown">
            <p v-if="show">hello</p>
        </transition>-->
    </div>
</template>

<script>
import VueFileUpload from 'vue-file-upload';
import ProgressBar from './progress-bar.vue';

const UPLOADING = 0;
const UPLOAD_SUCCESS = 1;
const UPLOAD_FAIL = 2;

export default{
    name: "c-upload-file",
    data(){
        let v = this;
        let rtn = {
            // vue-file-upload variables
            file: null,
            // file filter, jar file only
            filters:[
                {
                    name:"imageFilter",
                    fn(file){
                        var type = '|' + file.type.slice(file.type.lastIndexOf('/') + 1) + '|';
                        return '|x-java-archive|'.indexOf(type) !== -1;
                    }
                }
            ],
            // callback functions binding
            cbEvents: {
                onCompleteUpload(file,response,status,header){
                    let success = false;
                    if(status == 200 && response.code == 200){
                        success = true;
                    }
                    v._onCompeleteUpload(success);
                },
                onErrorUpload(file, response){
                    v._onErrorUpload();
                },
                onProgressUpload(file, progress){
                    v._onProgressUpload(progress);
                }
            },
            // request options
            reqopts: {
                formData:{
                    mc_version: null,
                    file_version: null,
                    description: null,
                    core_type: null
                },
                responseType:'json',
                withCredentials:false
            },
            // internal v-modal
            file_name: "",
            core_type: 'vanilla',
            minecraft_version: "",
            core_version: "",
            note: "",
            show_progress_bar : false,
            progress_bar_ratio : 0.0,
            progress_bar_status: UPLOADING
        }

        return rtn;
    },
    computed:{
        file_name(){
            if(this.file != null){
                return this.file.name;
            }else{
                return "";
            }
        },
        _enable_upload(){
            if(this.file_name.length > 0 && (""+this.minecraft_version).length > 0){
                return true;
            }else{
                return false;
            }
        }
    },
    methods:{
        onAddItem(files){
            this.file = files[files.length-1];
        },
        uploadItem(){
            // init formData
            let v = this;
            let values = {
                mc_version: v.minecraft_version,
                file_version: v.core_version,
                description: v.note,
                core_type: v.core_type
            }
            for(let key in values){
                this.reqopts.formData[key] = values[key];
            }
            this._enable_upload = false;
            this.show_progress_bar = true;
            this.file.upload();
        },
        // used when showing the modal
        resetForm(){
            this.file_name = "";
            this.core_type = "vanilla";
            this.minecraft_version = "";
            this.core_version = "";
            this.note = "";
            this.show_progress_bar = false;
            this.progress_bar_ratio = 0.0;
            this.progress_bar_status = UPLOADING;
        },
        _onCompeleteUpload(status){
            if(status){
                this.progress_bar_ratio = 1;
                this.progress_bar_status = UPLOAD_SUCCESS;
                this.$emit("uploadFinish");
            }else{
                this._enable_upload = true;
                this.progress_bar_ratio = 0.0;
                this.progress_bar_status = UPLOAD_FAIL;
            }
        },
        _onErrorUpload(){
            this._enable_upload = true;
            this.progress_bar_ratio = 0.0;
            this.progress_bar_status = UPLOAD_FAIL;
        },
        _onProgressUpload(progress){
            this.progress_bar_ratio = progress / 100;
        }
    },
    components:{
        'vue-file-upload': VueFileUpload,
        'progress-bar' : ProgressBar
    },
    // when everything is ready
    mounted(){
        let v = this;
        this.$watch('_enable_upload', (val, oldVal)=>{
            if(val === !oldVal)
                this.$emit("allowUpload", val)
        });
        // add callback events

    }
}
</script>

<style scoped>
div.edit_model_content div.form_group{
    line-height: 2em;
    font-size: 1.5rem;
    margin-top: 1.2rem;
    margin-bottom: 1.2rem;
}

div.edit_model_content div.form_label{
    position: relative;
    float:left;
    min-width: 8rem;
    width: 25%;
}

div.edit_model_content div.form_input{
    width: 100%;
    padding-left: 25%;
}

div.error-hint{
    font-size: 1.25rem;
    text-align: right;
    color: red;
}

input.input-file-name{
    width: 55%;
    display:inline-block;
}

i.notice-icon{
    color: cornflowerblue;
}

i.red-multiple{
    color: red;
}

i.red-multiple:before{
    content: "*"
}

</style>
