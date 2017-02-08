<template lang="html">
    <div class="wrap">
        <div class="row">
            <div class="col-md-2">
                <div class="box box-default box-solid">
                    <div class="box-header with-border">
                        <h3 class="box-title" style="font-size: 16px;">编辑信息</h3>
                    </div>

                    <div class="box-body no-padding" style="display:block">
                        <div class="conf_category">fef</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import WebSocket from "../../lib/websocket";
export default {
    data(){
        return {

        }
    },
    mounted(){
        console.log(this.$route.params.id);
    }
}
</script>

<style>
div.wrap{
    margin-top: 2rem;
    padding-left: 1rem;
}

div.no-padding{
    padding: 0 !important;
}
div.conf_category{
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
    padding-left: 1.5rem;
    border-bottom: 1px solid #dedede;
    box-sizing: border-box;
    height: 4rem;
    line-height: 3.5rem;
}

div.set_item.selected{
    border-left: 3px solid orange;
    font-weight: bold;
}
</style>
