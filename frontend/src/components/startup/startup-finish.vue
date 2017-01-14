<template lang="html">
    <div>
        <hr>
            <div class="finish-msg">
                很好，很清真。<br><b><span id="time">{{ count_down }}</span></b> 秒后将会跳转至登录界面。
            </div>
        <hr>
    </div>
</template>

<script>
    export default {
        data(){
            return {
                count_down : 5,
            }
        },
        computed:{
        },
        methods:{
        },
        mounted(){

        }
    };
</script>

<style scoped>
div.finish-msg{
    text-align: center;
    color: #333;
    margin-top: 2.5rem;
    margin-bottom: 2.5rem;
    font-size: 1rem;
    line-height: 1.5em;
}
</style>
