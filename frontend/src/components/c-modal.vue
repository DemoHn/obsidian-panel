<template>
    <transition name="modal">
        <div class="modal-mask">
            <div class="modal-wrapper">
                <div class="modal-content">

                    <div class="modal-header">
                        <slot name="header">
                            Header
                        </slot>
                    </div>

                    <div class="modal-body">
                        <slot name="body">
                            Body
                        </slot>
                    </div>

                    <div class="modal-footer">
                        <button class="btn btn-default pull-left" @click="$emit('cancel')" :disabled="cancel_btn_disabled">
                            <slot name="cancel_text">
                                Cancel
                            </slot>
                        </button>
                        <button class="btn btn-primary pull-right" @click="$emit('confirm')" :disabled="confirm_btn_disabled">
                            <slot name="confirm_text">
                                OK
                            </slot>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </transition>
</template>
<script>
    export default {
        props: {
            "cancel_btn_disabled":{
                type: Boolean,
                default: false
            },
            "confirm_btn_disabled":{
                type: Boolean,
                default: false
            }
        },
        data(){
            return {
                showModal : false
            }
        }
    }
</script>

<style>
.modal-mask {
    position: fixed;
    z-index: 9998;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, .5);
    display: table;
    transition: opacity .3s ease;
}

.modal-wrapper {
    display: table-cell;
    vertical-align: middle;
}

.modal-content {
    width: 450px;
    margin: 0px auto;
    background-color: #fff;
    border-radius: 2px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
    transition: all .3s ease;
    font-family: Helvetica, Arial, sans-serif;
}

.modal-header span{
    font-size: 1.8rem;
    font-weight: bold;
}

@media(max-width: 767px){
    .modal-content{
        width: 100%;
        margin: 0px auto;
    }
}

.modal-header h3 {
    margin-top: 0;
    color: #42b983;
}

/*
 * The following styles are auto-applied to elements with
 * transition="modal" when their visibility is toggled
 * by Vue.js.
 *
 * You can easily play with the modal transition by editing
 * these styles.
 */

.modal-enter {
    opacity: 0;
}

.modal-leave-active {
    opacity: 0;
}

.modal-enter .modal-content,
.modal-leave-active .modal-content {
    -webkit-transform: scale(1.1);
    transform: scale(1.1);
}
</style>
