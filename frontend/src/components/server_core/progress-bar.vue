<template lang="html">
    <div class="pg-hint">
        <div class="pg-label">
            <span class="upload-label text-left colored" v-if="status == 0">{{ label_uploading }}</span>
            <span class="upload-label text-left" v-if="status == 1">{{ label_success }}</span>
            <span class="upload-label text-left colored-error" v-if="status == 2">{{ label_fail }}</span>

            <span class="percent text-right colored">{{progress_percent}}</span>
        </div>
        <div class="pg-bar progress progress-xs active">
            <div class="progress-bar progress-bar-primary progress-bar-striped" :style="{width: progress_percent}"></div>
        </div>
    </div>
</template>

<script>
    const UPLOADING = 0;
    const UPLOAD_SUCCESS = 1;
    const UPLOAD_FAIL = 2;
    export default{
        name:'progress-bar',
        props: {
            'progress':{
                default: 0.0,
            },
            'status':{
                default: 2,
            },
            'label_success':{
                default: "Upload Succeed",
                type: String
            },
            'label_fail':{
                default: "Upload Fail",
                type: String
            },
            'label_uploading':{
                default: "Uploading...",
                type: String
            }

        },

        computed:{
            progress_percent(){
                return Math.floor(this.progress * 100) + "%"
            }
        }

    }
</script>

<style>
div.pg-hint{
    width: 100%;
}

div.pg-hint div.pg-label{
    position: relative;
    margin-top: 0.8rem;
    height: 1.3rem;
    margin-bottom: 0.8rem;
}
div.pg-label span.upload-label{
    display: inline-block;
    float: left;
    position:relative;
    font-size: 1.3rem;
}

div.pg-label span.percent{
    display: inline-block;
    float: right;
    position:relative;
    font-size: 1.3rem;
}

.colored{
    color: darkblue;
}

.colored-error{
    color: red;
}
</style>
