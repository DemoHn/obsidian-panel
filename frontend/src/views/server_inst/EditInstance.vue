<template lang="html">
    <div>
        <div class="row">
            <div class="col-md-3">
                <div class="box box-default box-solid">
                    <div class="box-header with-border">
                        <h3 class="box-title">Expandable</h3>
                    </div>

                    <div class="box-body" style="display:block">
                        hh
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

</style>
