<template lang="html">
        <quill-editor
            ref="Quill"
            :content="content"
            :config="editorOption"
            >
        </quill-editor>
</template>

<script>
import { quillEditor } from 'vue-quill-editor';
const motd_colors = [
    "#000000", "#0000be", "#00be00", "#00bebe", "#be0000",
    "#be00be", "#d9a334", "#bebebe", "#3f3f3f", "#3f3ffe",
    "#3ffe3f", "#3ffefe", "#fe3f3f", "#fe3ffe", "#fefe3f", "#ffffff"
];
const toolbarOptions = [
    ['bold', 'italic', 'underline', 'strike'],
    [{ 'color': motd_colors }]
];
const placeholders = ["这是一个Minecraft服务器，嗯。","I'm angry!","This server is young, simple and naive!"];
export default {
    name:"motd-editor",
    components:{
        'quill-editor': quillEditor
    },
    props:{
        "placeholder" : {
            default : placeholders[1]
        }
    },
    data(){
        return {
            content : "",
            editorOption:{
                modules : {
                    toolbar: toolbarOptions
                },
                placeholder : this.placeholder,
                theme:'snow'
            }
        }
    },
    methods:{
        // $ref API
        parse(){
            let contents = this.$refs.Quill.quillEditor.getContents().ops;

            let utf8_encode = (str) => {
                let f_str = "";
                let num = 0;
                for(let i=0;i<str.length;i++){
                    num = str.charCodeAt(i);
                    if(num > 0 && num < 128){
                        f_str += str[i];
                    }else{
                        hex_code = num.toString(16);
                        f_str += "\\u";
                        for(let j=0;j<4-hex_code.length;j++){
                            f_str += "0"
                        }

                        f_str += hex_code;
                    }
                }

                return f_str;
            }

            let SS = (R) => {
                let ss = "\\u00a7" + R; //§
                return ss;
            }

            let parsed_string = "";
            let _count = 0;
            let attribute_table = [];

            // generate attribute table
            for(let i = 0;i < contents.length;i++){
                let attr_arr = [];
                if(contents[i].hasOwnProperty("attributes") == false){
                    attr_arr.push("r");
                }else{
                    let attr = contents[i]["attributes"];
                    attr_arr.push("r");
                    //color
                    if(attr.hasOwnProperty("color")){
                        for(let k = 0;k<motd_colors.length;k++){
                            if(attr["color"] == motd_colors[k]){
                                attr_arr.push(k.toString(16));
                                //parsed_string += SS(k.toString(16)) + utf8_encode(text);
                            }
                        }
                    }
                    if(attr.hasOwnProperty("bold")){
                        if(attr["bold"] === true){
                            attr_arr.push("l");
                        }
                    }
                    if(attr.hasOwnProperty("strike")){
                        if(attr["strike"] === true){
                            attr_arr.push("m");
                        }
                    }
                    if(attr.hasOwnProperty("italic")){
                        if(attr["italic"] === true){
                            attr_arr.push("o");
                        }
                    }
                    if(attr.hasOwnProperty("underline")){
                        if(attr["underline"] === true){
                            attr_arr.push("n");
                        }
                    }
                }
                attribute_table.push(attr_arr);
            }

            // then, use attribute table to parse string
            for(let k=0;k<attribute_table.length;k++){
                for(let l=0;l<attribute_table[k].length;l++){
                    parsed_string += SS(attribute_table[k][l])
                }
                parsed_string += utf8_encode(contents[k]["insert"])
            }

            let chop_arr = parsed_string.split("\n");

            if(chop_arr.length == 0){
                return "";
            }else if(chop_arr.length == 1){
                return chop_arr[0];
            }else{
                if(chop_arr[1].length > 0){
                    return chop_arr[0] + "\n" + chop_arr[1];
                }else{
                    return chop_arr[0];
                }
            }
        }
    }
}
</script>

<style>
div.quill-editor{
    height: 5em;
    font-size: 15px;
}
</style>
