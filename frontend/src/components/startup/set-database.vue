<template lang="html">
    <div>
        <div class="hint_text"><b>STEP II:</b> 数据库环境设置</div>
        <hr>
        <p>请选择数据库环境：</p>
        <div>
            <md-radio v-model="db_type" name="db_type" md-value="sqlite">SQLite (推荐)</md-radio><br>
            <md-radio v-model="db_type" name="db_type" md-value="mysql">MySQL</md-radio>
        </div>

        <div id="mysql-account" style="margin-left:3em;" v-show="db_type == 'mysql'">
            <p><cite>请输入MySQL数据库的用户名和密码：</cite></p>
            <md-input-container md-inline>
                <md-icon><i class="ion-person"></i></md-icon>
                <label>用户名</label>
                <md-input v-model="mysql_username"></md-input>
            </md-input-container>
            <md-input-container md-inline>
                <md-icon><i class="ion-locked"></i></md-icon>
                <label>密码</label>
                <md-input v-model="mysql_password" type="password"></md-input>
            </md-input-container>

            <div>
                <md-button class="md-raised md-dense" type="button" v-on:click="test_connection" :disabled="!test_btn_enable">测试</md-button>
                &nbsp;&nbsp;
                <span style="color:red;display:inline-block;margin-top:12px;">
                    <span v-if="connection_result == 1">连接成功</span>
                    <span v-if="connection_result == 0">连接失败</span>
                    <span v-if="connection_result == -1">未知错误</span>
                </span>
            </div>
        </div>

        <div style="text-align: right;">
            <md-button class="md-raised md-primary" :disabled="!test_btn_enable">下一步</md-button>
        </div>
    </div>
</template>

<script>
    import Vue from "vue";
    import Resource from 'vue-resource';
    Vue.use(Resource);

    let ajax = (method, url, data, on_success, on_fail) => {
        const ajax_info = {
            url: url,
            method: method,
            body: data
        };

        if(typeof(data) == "function"){
            on_fail    = on_success;
            on_success = data;
        }

        let vs = null;
        if(method == "GET"){
            vs = Vue.http.get(url);
        }else if(method == "POST"){
            vs = Vue.http.post(url, data);
        }
        vs.then((response)=>{
            try{
                let body = JSON.parse(response.body);
                if(body.status == "success"){
                    if(typeof(on_success) == "function"){
                        on_success(body["info"]);
                        return ;
                    }
                }else{
                    // not login
                    if(body.code == 403){
                        window.location.href = "/super_admin/login";
                        return ;
                    }
                    if(typeof(on_fail) == "function"){
                        on_fail(body["code"]);
                        return ;
                    }
                }
            }catch(e){
                if(typeof(on_fail) == "function"){
                    const error_code = 500;
                    on_fail(500);
                    return ;
                }
            }
        },(response)=>{
            if(typeof(on_fail) == "function"){
                on_fail(500);
                return ;
            }
        })
    }
    export default {
        data(){
            return {
                connection_result : null,
                test_btn_enable: false,
                db_type : "sqlite",
                mysql_username :"",
                mysql_password : ""
            }
        },
        computed:{
            test_btn_enable() {
                return !!(this.mysql_password.length > 0 &&
                            this.mysql_username.length > 0);
            },
        },
        methods:{
            test_connection() {
                let self = this;
                let payloads = {
                    "mysql_username" : this.mysql_username,
                    "mysql_password" : this.mysql_password
                };

                ajax("POST", "/startup/test_mysql_connection",payloads, (msg) => {
                    if(msg){
                        self.connection_result = 1;
                    }else{
                        self.connection_result = 0;
                    }
                },(code) => {
                    self.connection_result = -1;
                });
            }
        },
        mounted(){

        }
    };
</script>

<style>
.md-radio{
    margin-top: 6px;
    margin-bottom: 6px;
}

.md-input-container{
    margin-bottom: 2px;
}

p{
    color : #666;
    margin-top: 12px;
    margin-bottom:6px;
}
</style>
