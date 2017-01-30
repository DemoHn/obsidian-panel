<template lang="html">
    <section class="content">
        <div class="row">
            <div class="col-md-5">
                <div class="box box-info">
                    <div class="box-header with-border">
                        <h3 class="box-title">基本信息</h3>
                        <div class="box-tools pull-right">
                            <button class="btn btn-box-tool" type="button" data-widget="collapse">
                                <i class="fa fa-minus"></i>
                            </button>
                        </div>
                    </div>
                    <div class="box-body">
                        <span class="sub_title">CPU信息</span>
                        <div class="sub_content">
                            <div class="_row">
                                <span class="sub_label">生产商</span>
                                <span class="info" v-if="CPU_vendor_info != ''">{{ CPU_vendor_info }}</span>
                                <span class="gray" v-else>未知</span>
                            </div>
                            <div class="_row">
                                <span class="sub_label">型号</span>
                                <span class="info" v-if="CPU_model_info != ''">{{ CPU_model_info }}</span>
                                <span class="gray" v-else>未知</span>
                            </div>
                            <div class="_row">
                                <span class="sub_label">核数</span>
                                <span class="info" v-if="CPU_cores_info != ''">{{ CPU_cores_info }}</span>
                                <span class="gray" v-else>未知</span>
                            </div>
                            <div class="_row">
                                <span class="sub_label">主频</span>
                                <span class="info" v-if="CPU_freq_info != ''">{{ CPU_freq_info }}</span>
                                <span class="gray" v-else>未知</span>
                            </div>
                        </div>
                        <span class="sub_title">操作系统</span>
                        <div class="sub_content">
                            <div class="_row">
                                <span class="sub_label">类型</span>
                                <span class="info" v-if="OS_name_info != ''">{{ OS_name_info }}</span>
                                <span class="gray" v-else>未知</span>
                            </div>
                            <div class="_row">
                                <span class="sub_label">版本</span>
                                <span class="info" v-if="OS_distro_info != ''">{{ OS_distro_info }}</span>
                                <span class="gray" v-else>未知</span>
                            </div>
                            <div class="_row">
                                <span class="sub_label">内核版本</span>
                                <span class="info" v-if="OS_kernel_info != ''">{{ OS_kernel_info }}</span>
                                <span class="gray" v-else>未知</span>
                            </div>
                            <div class="_row">
                                <span class="sub_label">架构</span>
                                <span class="info" v-if="OS_arch_info != ''">{{ OS_arch_info }}</span>
                                <span class="gray" v-else>未知</span>
                            </div>
                        </div>
                        <span class="sub_title">内存</span>
                        <div class="sub_content">
                            <div class="_row">
                                <span class="sub_label">总内存</span>
                                <span class="info" v-if="RAM_info != ''">{{ RAM_info }}</span>
                                <span class="gray" v-else>未知</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<script>
    import WebSocket from "../../lib/websocket.js"
    export default {
        data(){
            return {
                "CPU_model_info" : "",
                "CPU_vendor_info" :"",
                "CPU_cores_info" : "",
                "CPU_freq_info" : "",
                "OS_name_info" : "",
                "OS_arch_info" : "",
                "OS_distro_info" : "",
                "OS_kernel_info" : "",
                "RAM_info" : ""
            }
        },
        computed:{
            allow_password_amend(){
                if(this.ori_password.length > 0 && this.new_password.length > 0){
                    return true;
                }else{
                    return false;
                }
            }
        },
        methods:{
            aj_get_server_info(){
                let ws = new WebSocket();
                let v = this;
                ws.ajax("GET", "/super_admin/info/get_server_info", (msg)=>{
                    v.CPU_model_info = msg.cpu.model;
                    v.CPU_vendor_info = msg.cpu.vendor;
                    v.CPU_cores_info = msg.cpu.cores;
                    v.CPU_freq_info = msg.cpu.freq + " MHz";
                    v.OS_name_info = msg.OS.name;
                    v.OS_arch_info = msg.OS.arch;
                    v.OS_kernel_info = msg.OS.kernel;
                    v.OS_distro_info = msg.OS.distro;
                    v.RAM_info = msg.memory + " GiB";
                },(code)=>{
                });
            }
        },
        mounted(){
            this.aj_get_server_info();
        }
    }
</script>

<style scoped>
span.sub_title{
    display:inline-block;
    margin-top:0.5rem;
    font-weight: bold;
    font-size: 1.7rem;
    margin-bottom: 0.5rem;
}

div.sub_content{
    padding-left: 4rem;
}

span.gray{
    color: #777;
}
div._row{
    line-height: 2.2rem;
}

div._row span.sub_label{
    margin-right: 1rem;
    font-size: 1.5rem;
}

span.info{
    color: darkblue;
}
</style>
