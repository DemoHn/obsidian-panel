<template>
  <div>
    <router-view></router-view>
  </div>
</template>

<script>
    import WebSocket from "../lib/websocket.js";
    import BodyParser from '../lib/body-parser.js';
    export default {
        name: 'App',
        data: function () {
            return {

            }
        },
        methods: {
            /*NOTICE: this method is only suitable for this app since it contains automatic JSON parsing*/
            callAPI: function(method, url, data, on_success, on_fail){
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
                    vs = this.caller.get(url)
                }else if(method == "POST"){
                    vs = this.caller.post(url, data);
                }
                vs.then((response)=>{
                    try{
                        let body = JSON.parse(response.body);
                        if(body.status == "success"){
                            if(typeof(on_success) == "function")
                                on_success(body["info"]);
                        }else{
                            // not login
                            if(body.code == 403){
                                window.location.href = "/super_admin/login";
                                return ;
                            }
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
            }
        }
    }
    </script>
