<template lang="html">
    <div class="loading-mask">
        <div class="__child">
            <div class="loading-text loading-face">☹</div>
            <div class="loading-text">&nbsp;Error!</div>

        </div>
    </div>
</template>

<script>
    export default {
        name:"load-error"
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
    margin-top: 2rem;
}

div.loading-mask div.loading-text{
    font-size: 2rem;
}

div.loading-mask div.loading-face{
    font-size: 4rem;
}
</style>
