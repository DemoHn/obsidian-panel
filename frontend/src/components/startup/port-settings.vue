<template lang="html">
    <div>
        <div class="hint_text"><b>STEP III:</b> 端口设置</div>
        <hr>
        <div>
            <table class="tb">
                <tr>
                    <td class="lb"><span class="label"><b>网页端口</b></span></td>
                    <td>
                        <md-input-container md-inline>
                            <label>网页端口</label>
                            <md-input v-model="app_port" type="number"></md-input>
                        </md-input-container>
                    </td>
                </tr>
                <tr>
                    <td class="lb"><span class="label"><b>FTP端口</b></span></td>
                    <td>
                        <md-input-container md-inline>
                            <label>FTP端口</label>
                            <md-input v-model="ftp_port"></md-input>
                        </md-input-container>
                    </td>
                </tr>
                <tr><td colspan="2"><div style="text-align: center;margin-top: 1rem;color:#888;">以下端口为系统自用，如无意外，毋须更改</div></td></tr>
                <tr>
                    <td class="lb-wide"><span class="label"><i>Websocket Server</i></span></td>
                    <td>
                        <md-input-container md-inline>
                            <label>&lt;Internal Port&gt;</label>
                            <md-input v-model="ws_port"></md-input>
                        </md-input-container>
                    </td>
                </tr>
                <tr>
                    <td class="lb-wide"><span class="label"><i>MsgQ Broker</i></span></td>
                    <td>
                        <md-input-container md-inline>
                            <label>&lt;Internal Port&gt;</label>
                            <md-input v-model="msgQ_port"></md-input>
                        </md-input-container>
                    </td>
                </tr>

                <tr>
                    <td class="lb-wide"><span class="label"><i>Proc. Supervisor</i></span></td>
                    <td>
                        <md-input-container md-inline>
                            <label>&lt;Internal Port&gt;</label>
                            <md-input v-model="pm_port"></md-input>
                        </md-input-container>
                    </td>
                </tr>
            </table>
        </div>
        <div style="text-align: right;">
            <md-button class="md-raised md-primary" @click="submit" :disabled="!allow_submit">完成</md-button>
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
                app_port: 80,
                ftp_port: 21,
                msgQ_port: 852,
                ws_port:851,
                pm_port:853,
                allow_submit : false
            }
        },
        computed:{
            allow_submit(){
                let ports = [
                    this.app_port,
                    this.ftp_port,
                    this.msgQ_port,
                    this.ws_port,
                    this.pm_port
                ];

                let allow_submit = true;

                for(let i=0;i<ports.length;i++){
                    for(let j=i+1;j<ports.length;j++){
                        if(ports[i] == ports[j]){
                            return false;
                        }
                    }
                }
                return true;
            }
        },
        methods:{
            submit(){
                let _v = {
                    app_port: this.app_port,
                    ftp_port: this.ftp_port,
                    msgQ_port: this.msgQ_port,
                    ws_port:this.ws_port,
                    pm_port:this.pm_port
                }

                this.$emit("submit", _v);
            }
        },
        mounted(){
        }
    };
</script>

<style scoped>
.md-input-container{
    margin-bottom: 0 !important;
}

table.tb{
    width: 100% !important;
}

table td.lb{
    width: 4rem;
    vertical-align: middle;
}
table td.lb-wide{
    width: 7.5rem;
    vertical-align: middle;
}

table td.lb span.label,
table td.lb-wide span.label{
    display: inline-block;
    margin-top: 1rem;
}

p{
    color : #666;
    margin-top: 12px;
    margin-bottom:6px;
}
</style>
