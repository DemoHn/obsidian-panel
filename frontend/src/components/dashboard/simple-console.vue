<template lang="html">
    <div>
        <div class="embeded-console">
            <!--<vue-editor v-model="editor_content" @init="editorInit" theme="dawn" ref="editorComponent" width="100%" height="100%"></vue-editor>-->
            <pre class="console-pre"><code v-for="line in content_arr">{{ line }}</code></pre>
        </div>
        <div class="input_cmd_bar">
            <input type="text" class="input_cmd" v-model="command_content" @keyup.13="input_command"/>
            <div class="input_hint"><i class="ion-chevron-right"></i></div>
            <button class="btn_enter" @click="input_command">输入</button>
        </div>
    </div>
</template>

<script>
    export default {
        name:"simple-console",
        data(){
            return {
                content_arr : [],
                command_content : "",
                input_disabled : false
            }
        },
        methods:{
            scroll_to_bottom(){
                let container = this.$el.querySelector("div.embeded-console");
                container.scrollTop = container.scrollHeight;
            },
            // $ref API
            init_history_log(history_log){
                let _arr = history_log.split("\n");
                _arr = _arr.map((item)=>{
                    return item + "\n";
                })
                this.content_arr = _arr;
                let v = this;
                this.$nextTick(()=>{
                    v.scroll_to_bottom();
                })
            },
            // $ref API
            append_log(str){
                this.content_arr.push(str);
                let v = this;
                this.$nextTick(()=>{
                    v.scroll_to_bottom();
                })

            },
            input_command(){
                let command = this.command_content;
                if(command != null){
                    if(command.length > 0){
                        this.$emit("input", command);
                    }
                }
                //clear input
                this.command_content = "";
            }
        },
        mounted(){
        }
    }
</script>

<style scoped>
div.embeded-console{
    width: 100%;
    height: 25rem;
    overflow-y: auto;
    border-top: 1px solid #ccc;
    border-left: 1px solid #ccc;
    border-right: 1px solid #ccc;
    background-color: rgba(245,245,245, 0.8);
}

div.embeded-console pre{
    background-color: rgba(245,245,245, 0.8);
    border:none;
    border-radius: 0;
    margin: 0 !important;
    padding: 0.25rem 1rem !important;
    text-align:left;
    overflow-y: hidden;
    box-sizing: border-box;
    line-height: 1.3em;
}

code{
    font-size: 12px;
}
div.input_cmd_bar{
    height: 3rem;
    width: 100%;
    position: relative;
}

input.input_cmd{
    position:absolute;
    display: block;
    outline: none;
    height: 100%;
    border: none;
    width: 100%;
    box-sizing: border-box;
    background-color: #fcfcfc;
    border: 1px solid #ccc;
    line-height: 2em;
    font-size: 13px;
    padding-left: 2.5rem;
    font-family: "Monaco", "Consolas", monospace;
}

div.input_hint{
    position: absolute;
    width: 20px;/*ace's width*/
    padding-right:0.3rem;
    height: 100%;
    line-height: 3rem;
    text-align: right;
    font-size: 12px;
    color: gray;
}

button.btn_enter{
    position:absolute;
    right: 0;
    outline: 0;
    border: 1px solid #aaa;
    border-radius: 5px;
    font-size: 13px;
    display: inline-block;
    height: 2.2rem;
    margin: 0.3rem;
    margin-top:0.35rem;
    background-color: transparent;
}
</style>
