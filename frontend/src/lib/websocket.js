import Vue from "vue";
import Resource from 'vue-resource';

Vue.use(Resource);

const MAX_RETRY = 10;

// this is a hackable way to make a global
//window.WS_INSTANCE = null;
let instance = null;

class WebSocket {
    constructor(socket_port=5001){
        if(!instance){
            instance = this;

            this.socket = null;
            this.socket_port = socket_port;
            this._init();

            this.socketQueue = {};
            this.pendingFlags = {};
            this.bindEvents  = {};
            this.connected = false;
        }
        return instance;
    }

    _generate_flag(num=16){
        let series = "0123456789abcdefghijklmnopqrstuvwxyzZ";
        let str = "";
        for(var i=0;i<num;i++){
            str += series[Math.floor(Math.random() * 36)];
        }
        return str;
    }

    _get_current_host(){
        let http = location.protocol;
        let slashes = http.concat("//");
        let host = slashes.concat(window.location.hostname);
        return host;
    }

    _init(){
        if(io !== undefined){
            if(this.socket === null){
                this.socket = io.connect(this._get_current_host()+":"+this.socket_port);
            }

            this.socket.on("connect",(e)=>{
                this.connected = true;
            });

            this.socket.on("disconnect",(e)=>{
                this.connected = false;
            });

            this.socket.on("message", (msg)=>{
                if(this.socketQueue[msg.flag] != null){
                    let execFunc = this.socketQueue[msg.flag];

                    if(this.pendingFlags[msg.flag] != null){
                        this.pendingFlags[msg.flag] = -1;
                    }

                    execFunc(msg);
                    delete this.socketQueue[msg.flag];
                }

                // exec binded functions
                if(this.bindEvents[msg.event] != null){
                    let execFunc = this.bindEvents[msg.event];
                    execFunc(msg);
                }
            });
        }
    }

    // callback definition: callback_success(msg)
    send(event_name, props, callback_success, callback_timeout){
        const flag = this._generate_flag();

        if(props == null){
            props = {}
        }
        let send_json = {
            "event" : event_name,
            "flag" : flag,
            "props" : props
        };

        this.socket.emit("message", send_json);

        // if callback success is a function
        if(typeof(callback_success) == "function"){
            // if callback is set, that means this socket is waiting for response,
            // so auto-resending is considered when there is no response.
            this.pendingFlags[flag] = 0;
            this.socketQueue[flag] = callback_success;

            let v = this;
            let _f = flag;
            let interval_flag = setInterval(()=>{
                if(v.pendingFlags[_f] == -1){
                    clearInterval(interval_flag);
                    return ;
                }else if(v.pendingFlags[_f] < MAX_RETRY){
                    console.debug("resending msg: "+JSON.stringify(send_json));
                    v.socket.emit("message", send_json);
                    v.pendingFlags[_f] += 1;
                }else{
                    clearInterval(interval_flag);
                }
            },5000);
        }
    }

    bind(event_name, bind_func){
        if(typeof(bind_func) == "function"){
            this.bindEvents[event_name] = bind_func;
        }
    }

    ajax(method, url, data, on_success, on_fail){
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
}

export default WebSocket
