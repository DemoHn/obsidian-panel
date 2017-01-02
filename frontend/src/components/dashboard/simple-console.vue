<template lang="html">
    <div>
        <div class="embeded-console">
            <vue-editor v-model="editor_content" @init="editorInit" theme="dawn" ref="editorComponent" width="100%" height="100%"></vue-editor>
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
        components:{
            "vue-editor": require("vue2-ace-editor")
        },
        data(){
            return {
                editor_content : "",
                command_content : "",
                input_disabled : false
            }
        },
        methods:{
            editorInit:function () {
                require('vue2-ace-editor/node_modules/brace/theme/dawn');
                this._init_editor_config(this.$refs.editorComponent.editor);
            },

            _init_editor_config(editor){
                editor.$blockScrolling = Infinity;

                // set read only
                editor.setReadOnly(true);

                // set a light theme
                editor.setTheme("ace/theme/dawn");

                // not show line number
                editor.renderer.setOption('showLineNumbers', false);

                // set font size
                editor.setFontSize(12);
                editor.setShowPrintMargin(false);
                // wrap lines when a line is too long to show all
                editor.session.setOption('indentedSoftWrap', false);
                editor.session.setUseWrapMode(true);
            },

            // $ref API
            init_history_log(history_log){
                this.editor_content = history_log;
                let editor = this.$refs.editorComponent.editor;
                let row = editor.session.getLength();
                editor.gotoLine(row+1, 0);
            },
            // $ref API
            append_log(str){
                let editor = this.$refs.editorComponent.editor;
                editor.session.insert({
                    row: editor.session.getLength(),
                    column: 0
                }, str);

                // keep the cursor in the last line
                let row = editor.session.getLength();
                editor.gotoLine(row+1, 0);
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
    border-top: 1px solid #ccc;
    border-bottom: 1px solid #ccc;
    line-height: 2em;
    font-size: 13px;
    padding-left: 38px;
    font-family: "Monaco", "Consolas", monospace;
}

div.input_hint{
    position: absolute;
    width: 33px;/*ace's width*/
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
