<template>
  <div>
    <router-view></router-view>
  </div>
</template>

<script>
    import WebSocket from "../lib/websocket.js";
    export default {
        name: 'App',
        data: function () {
            return {
                section: 'Head',
                version: '0.10.0',
                callingAPI: false,
                serverURI: 'http://10.110.1.10:8080',
                ws : new WebSocket(5001),
                caller: this.$http // vue-resource
            }
        },
        methods: {
            /*NOTICE: this method is only suitable for this app since it contains automatic JSON parsing*/
            ajax: function(method, url, data, on_success, on_fail){
                const ajax_info = {
                    url: url,
                    method: method,
                    data: data
                };

                if(typeof(data) == "function"){
                    on_fail    = on_success;
                    on_success = data;
                }
                this.caller(ajax_info).then((response)=>{
                    // on success
                    try{
                        let body = JSON.parse(response.body);
                        if(body.status == "success"){
                            if(typeof(on_success) == "function")
                                on_success(body["info"]);
                        }else{
                            if(typeof(on_fail) == "function")
                                on_fail(body["code"]);
                        }
                    }catch(e){
                        if(typeof(on_fail) == "function"){
                            const error_code = 500;
                            on_fail(500);
                        }
                    }
                },(response)=>{
                    if(typeof(on_fail) == "function"){
                        on_fail(500);
                    }
                })
            },
            callAPI: function (method, url, data) {
                this.callingAPI = true
                url = url || this.serverURI // if no url is passed then inheret local server URI
                return this.caller({
                    url: url,
                    method: method,
                    data: data
                })
            },
            logout: function () {
                this.$store.dispatch('SET_USER', null)
                this.$store.dispatch('SET_TOKEN', null)

                if (window.localStorage) {
                    window.localStorage.setItem('user', null)
                    window.localStorage.setItem('token', null)
                }

                this.$router.push('/login')
            }
        }
    }
</script>
