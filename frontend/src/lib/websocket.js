class WebSocket {
    constructor(socket_port=5001){
        this.socket_port = socket_port;
        this._init();

        this.socketQueue = {};
        this.bindEvents  = {};
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
            this.socket = io.connect(this._get_current_host()+":"+this.socket_port);

            this.socket.on("connect",(e)=>{
                console.log("hello");
            });

            this.socket.on("message", (msg)=>{
                if(this.socketQueue[msg.flag] != null){
                    let execFunc = this.socketQueue[msg.flag];
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
            this.socketQueue[flag] = callback_success;
        }
    }

    bind(event_name, bind_func){
        if(typeof(bind_func) == "function"){
            this.bindEvents[event_name] = bind_func;
        }
    }
}

export default WebSocket
