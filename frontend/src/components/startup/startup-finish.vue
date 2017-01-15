<template lang="html">
    <div>
        <hr>
            <div class="finish-msg">
                很好，很清真。<br><b><span id="time">{{ count_down }}</span></b> 秒后将会跳转至登录界面。
            </div>
        <hr>
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
                count_down : 5,
            }
        },
        mounted(){
            ajax("GET", "/startup/__reboot", ()=>{});
            let v = this;
            let _interval = setInterval(()=>{
                v.count_down -= 1;
                if(v.count_down == 0){
                    clearInterval(_interval);
                    // redirect to login page
                    window.location.href = "/login"
                }
            }, 1000)
        }
    };
</script>

<style scoped>
div.finish-msg{
    text-align: center;
    color: #333;
    margin-top: 2.5rem;
    margin-bottom: 2.5rem;
    font-size: 1rem;
    line-height: 1.5em;
}
</style>
