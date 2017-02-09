<template lang="html">
    <div class="edit-item">
        <div class="item-title">
            <span class="title">
                <slot name="title">Default Title</slot>
            </span>
            <span class="item-status">
                <span v-show="JR_status == 0">
                    <slot name="JR_loading"><i class="fa fa-spinner fa-spin fa-fw" style="color: darkblue;"></i></span></slot>
                </span> <!-- loading -->
            <span v-show="JR_status == 1">
                <slot name="JR_error">
                    <i class="ion-close-round" style="color: red;"></i>
                </slot>
            </span><!-- error -->
            <span v-show="JR_status == 2">
                <slot name="JR_error">
                    <i class="ion-checkmark-round" style="color: green;"></i>
                </slot>
            </span> <!-- success -->
        </div>
        <div class="description">
            <slot name="description"></slot>
        </div>
        <div class="item-body">
            <slot name="body"></slot>
        </div>
    </div>
</template>

<script>
    export default {
        name : "edit-item",
        props: {
            JR_status : {
                default : null
            }
        },
        computed:{

        },
        data(){
            return {
            }
        }
    }
</script>
<style scoped>
div.item-title{
    width: 100%;
}

div.description{
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
    font-size: 13px;
    color: #666;
}

div.item-body{
    padding-top:0.5rem;
    padding-bottom: 0.5rem;
}
div.item-title span.title{
    font-size: 1.7rem;
    color: #813cb2;
    display: inline-block;
    margin-right: 1rem;
}

div.item-title span.item-status{
    font-size: 1.5rem;
}
div.edit-item{
    border-bottom: 1px solid #ececec;
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
}


</style>
