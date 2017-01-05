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
        computed:{

        }
    }
</script>

<style>
div.quill-editor{
    height: 5em;
    font-size: 15px;
}
</style>
