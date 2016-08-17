// javascript file for super_admin
Vue.config.delimiters = ['${','}'];

$(document).ready(function(){
    // tooltip initialization
    //$("#_logout").tooltip();
    var socket = io.connect("/dw");
    console.log("connect:")
    socket.on("connect", function () {
        console.log("f")
        socket.emit("hw",{'a':'b'})
    })

    socket.on("oh",function (msg) {
        console.log(msg);
    })
});