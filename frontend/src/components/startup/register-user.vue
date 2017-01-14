<template lang="html">
    <div>
        <div class="hint_text">欢迎使用「黑曜石面板」!<br><b>STEP I:</b> 注册管理员账号</div>
        <hr>
        <md-input-container md-inline>
            <md-icon><i class="ion-person"></i></md-icon>
            <label>用户名</label>
            <md-input v-model="username"></md-input>
        </md-input-container>
        <div class="error-msg" v-if="empty_username">用户名不能为空！</div>
        <div class="error-msg" v-if="hasi_username">思维江化，亦可赛艇Θ..Θ</div>
        <md-input-container md-inline>
            <md-icon><i class="ion-email"></i></md-icon>
            <label>E-mail</label>
            <md-input v-model="email"></md-input>
        </md-input-container>
        <div class="error-msg" v-if="email_empty">E-mail 不能为空！</div>
        <div class="error-msg" v-if="email_error">E-mail 不合规范！</div>

        <md-input-container md-inline>
            <md-icon><i class="ion-locked"></i></md-icon>
            <label>密码</label>
            <md-input type="password" v-model="password"></md-input>
        </md-input-container>
        <div class="error-msg" v-if="password_error">密码长度在6-30位之间！</div>

        <md-input-container md-inline>
            <md-icon><i class="ion-locked"></i></md-icon>
            <label>重复密码</label>
            <md-input type="password" v-model="repeat_password"></md-input>
        </md-input-container>
        <div class="error-msg" v-if="repeat_error">前后密码不一致！</div>

        <div style="text-align: right;">
            <md-button class="md-raised md-primary" :disabled="!agree">下一步</md-button>
        </div>
    </div>
</template>

<script>
    export default {
        data(){
            return {
                "username":"",
                "email":"",
                "password":"",
                "repeat_password":"",
                "hasi_username" : false,
                "empty_username" : false,
                "email_error": false,
                "email_empty": false,
                "password_error": false,
                "repeat_error": false,
                "agree" : true
            }
        },
        computed:{
            "hasi_username" : function () {
                var excited_words = ["excited","+1s","plus+1s","蛤","naive","too young","too simple","hawaii guitar","engineering drawing"];
                for(var i=0;i<excited_words.length;i++){
                    if(this.username == excited_words[i]){
                        return true;
                    }
                }
                return false;
            },
            "password_error": function () {
                var len = this.password.length;
                if(len > 0 && (len < 6 || len > 30)){
                    return true;
                }else{
                    return false;
                }
            },
            "repeat_error": function () {
                if(this.repeat_password.length > 0 && this.repeat_password !== this.password){
                    return true;
                }else{
                    return false;
                }
            },
            "agree":function () {
                if(
                    ! this.repeat_error &&
                    ! this.hasi_username &&
                    ! this.password_error
                ){
                    var re_email = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/i;
                    if(this.username.length > 0 &&
                       re_email.test(this.email) &&
                       this.password.length > 0 && // password not null
                       this.password === this.repeat_password
                      ){
                        return true;
                    }else{
                        return false;
                    }
                }else{
                    return false;
                }
            }
        },
        methods:{

        },
        mounted(){

        }
    };
</script>

<style>
div.error-msg{
    background-color: #dd4b39;
    padding: 8px 15px;
    color: white;
}

div.hint_text{
    text-align: center;
    color: #666;
}
</style>
