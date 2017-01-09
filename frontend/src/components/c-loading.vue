<template lang="html">
    <div class="loading-mask">
        <div class="__child">
            <i class="fa fa-circle-o-notch fa-spin fa-3x fa-fw"></i>
            <div class="loading-text">&nbsp;Loading...</div>
        </div>
    </div>
</template>

<script>
    export default {
        name:"c-loading"
    }
</script>

<style scoped>
div.loading-mask{
    min-height: 12rem;
    width: 100%;
    text-align: center;
    vertical-align: middle;
    color: #a3a3a3;
}

div.loading-mask div.__child{
    margin-top: 6rem;
}

div.loading-mask div.loading-text{
    margin-top: 0.5rem;
    font-size: 2rem;
}
</style>
