<template lang="html">
    <li>
        <!-- timeline icon -->
        <i class="fa fa-check bg-green" v-if="JR_result === true"></i>
        <i class="fa fa-close bg-red" v-else-if="JR_result === false"></i>
        <i class="fa" v-else></i>
        <div class="timeline-item col-md-5">
            <span class="time" v-show="required">必需</span>
            <div class="error-msg" v-show="JR_result === false">
                <slot name="error-msg">ERROR</slot>
            </div>
            <h3 class="timeline-header">
                <slot name="title">Default Title</slot>
            </h3>
            <div class="timeline-body">
                <slot name="control">
                </slot>
            </div>
        </div>
        <div class="col-md-3 description">
            <slot name="description">

            </slot>
        </div>
    </li>
</template>

<script>
    export default {
        name : "inst-item",
        props: {
            required : {
                default: true,
            },
            JR_result : {
                default : null
            }
        },
        computed:{
            model_data(){
                return this.model;
            }
        },
        data(){
            return {
            }
        }
    }
</script>

<style scoped>
div.description{
    margin-left: 43px;
    color: #666;
    font-size: 1.6rem;
}

span.time{
    color: darkred !important;
}

.timeline-header{
    font-size: 1.5rem !important;
    color: darkblue !important;
}

div.error-msg{
    position: absolute;
    display: inline-block;
    padding:2px 10px;
    margin:6px;
    right:0;
    top: 0;
    background-color: #dd4b39;
    color: white;
    margin-right: 5px;

}
div.timeline-body input[type="text"],
div.timeline-body input[type="password"]{
    border:none;
    width:100%;
    outline: none;
    font-size: 1.8rem;
}

@media(max-width: 766px){
    div.description{
        display: none;
    }
}
</style>
