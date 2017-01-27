<template lang="html">
    <section class="content">
        <div class="row">
            <div class="col-md-5">
                <div class="box box-info">
                    <div class="box-header with-border">
                        <h3 class="box-title">设置</h3>

                        <div class="box-tools pull-right">
                            <button class="btn btn-box-tool" type="button" data-widget="collapse">
                                <i class="fa fa-minus"></i>
                            </button>
                        </div>
                    </div>
                    <div class="box-body" id="password_settings">
                        <span class="sub_title">管理员密码</span>
                        <div class="sub_content">
                            <span class="des">重新设置管理员密码</span>
                            <div>
                                <span class="sub_label">旧密码</span>
                                <input
                                    type="password"
                                    class="form-control narrow-width"
                                    v-model="ori_password" />
                            </div>
                            <br>
                            <div>
                                <span class="sub_label">新密码</span>
                                <input
                                    type="password"
                                    class="form-control narrow-width"
                                    v-model="new_password" />
                            </div>
                            <br>
                            <div>
                                <button class="btn btn-primary btn-sm" :disabled="!allow_password_amend" @click="aj_amend_password">修改</button>
                                <span class="hint" v-if="amend_password_result == 1">修改密码成功</span>
                                <span class="hint" v-if="amend_password_result == 2">修改密码失败</span>
                            </div>
                            <br>
                        </div>

                        <span class="sub_title">软件更新</span>
                        <div class="sub_content">
                            
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
                "ori_password": "",
                "new_password": "",
                "amend_password_result" : null
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
            aj_amend_password(){
                let ws = new WebSocket();
                let payload = {
                    "ori_password" : this.ori_password,
                    "new_password" : this.new_password
                };
                ws.ajax("POST", "/super_admin/settings/passwd", payload, (msg)=>{
                    this.amend_password_result = 1;
                },(code)=>{
                    this.amend_password_result = 2;
                });
            }
        },
        mounted(){
            
        }
    }
</script>

<style scoped>
span.sub_title{
    display:inline-block;
    margin-top:0.5rem;
    font-weight: bold;
    font-size: 15px;
}

span.des{
    font-size: 13px;
    color: gray;
    margin-bottom:1rem;
    margin-top: 0.5rem;
    display:inline-block;
}

span.sub_label{
    display:inline-block;
    font-size: 14px;
    margin-right: 3rem;
}
div.sub_content{
    width:100%;
    padding-left: 3rem;
}

input.narrow-width{
    max-width: 20rem;
    display: inline-block;
}

span.hint{
    display: inline-block;
    margin-left: 1rem;
    color: darkblue;
}
</style>
