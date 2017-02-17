<template lang="html">
    <div v-html="_raw_content"></div>
</template>

<script>
    export default {
        name : "motd-display",
        props : {
            content : {
                default : ""
            }
        },
        data(){
            return {
                _raw_content : ""
            }
        },
        computed : {
            _raw_content(){
                return this.display();
            }
        },
        methods : {
            display(){
                function _format_style_string(char_code){
                    const motd_colors = [
                        "#000000", "#0000be", "#00be00", "#00bebe", "#be0000",
                        "#be00be", "#d9a334", "#bebebe", "#3f3f3f", "#3f3ffe",
                        "#3ffe3f", "#3ffefe", "#fe3f3f", "#fe3ffe", "#fefe3f", "#ffffff"
                    ];

                    if(/^[0-9a-fA-F]$/.test(char_code)){
                        return "color : " + motd_colors[parseInt(char_code, 16)] + ";";
                    }else if(char_code == "l"){
                        return "font-weight: bold;";
                    }else if(char_code == "m"){
                        return "text-decoration: line-through;";
                    }else if(char_code == "o"){
                        return "font-style: italic;";
                    }else if(char_code == "n"){
                        return "text-decoration: underline;";
                    }else{
                        return "";
                    }
                }

                let motd_string = this.content;
                //encode data
                motd_string = motd_string.replace(/&/g, "&amp;");
                motd_string = motd_string.replace(/</g, "&lt;");
                motd_string = motd_string.replace(/>/g, "&gt;");
                // decode into utf-mode
                motd_string = motd_string.replace(/\\u([0-9a-fA-F]{4})/g, function(match, p1){
                    return String.fromCharCode(parseInt(p1, 16));
                });

                motd_string = motd_string.trim();

                // then add format
                var format_table = motd_string.split("§r");

                var formatted_string = "";
                for(var i=0;i<format_table.length;i++){
                    var _text = format_table[i];
                    var f_arr = [];

                    if(_text.length > 0){
                        if(/§([0-9a-flmon])/gi.test(_text) == true){
                            f_arr = /§([0-9a-flmon])/gi.exec(_text);
                        }
                        _text = _text.replace(/§([0-9a-flmon])/gi, "");
                        for(var j=1;j<f_arr.length;j++){
                            _text = "<span style='" + _format_style_string(f_arr[j]) + "'>" + _text + "</span>";
                        }
                        formatted_string += _text;
                    }
                }
                return formatted_string;
            }
        }
    }
</script>

<style>

</style>
