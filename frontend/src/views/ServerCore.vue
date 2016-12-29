<template lang="html">
    <section class="content">
        <div class="row">
            <div class="col-md-6 col-lg-6">
                <div class="box box-info">
                    <div class="box-header with-border">
                        <h3 class="box-title">核心文件管理</h3>
                        <div class="box-tools pull-right">
                            <button class="btn btn-box-tool" type="button" data-widget="collapse">
                                <i class="fa fa-minus"></i>
                            </button>
                        </div>
                    </div>
                    <div class="box-body">
                        <div v-if="status == 2">
                            <load-error></load-error>
                        </div>
                        <div v-if="status == 0">
                            <c-loading></c-loading>
                        </div>
                        <div v-if="status == 1">
                            <div v-if="core_list.length == 0">
                                <div class="core_nothing">这里空空如也 <br /> 点击下面的「添加」按钮以添加核心</div>
                            </div>
                            <div class="core_list" v-for="(core_item,_index) in core_list">
                                <div class="edit-button">
                                    <a title="" data-placement="left" data-toggle="tooltip"  data-original-title="编辑" @click="edit_serv_core(_index)"><i class="ion-edit"></i></a>
                                    <a title="" data-placement="left" data-toggle="tooltip" data-original-title="删除" @click="delete_serv_core(_index)"><i class="ion-close-round"></i></a>

                                </div>
                                <div class="server_core_avatar">

                                </div>

                                <div class="server_core_info">
                                    <div class="list_title">
                                        {{ core_item.file_name }}
                                    </div>
                                    <div class="list_row">
                                        <div class="half">
                                            <span class="ttl">类型: </span>
                                            <span class="default-text" v-if="core_item.core_type.toLowerCase() == 'others'">其他</span>
                                            <span class="text" v-else>{{ core_item.core_type }}</span>
                                        </div><div class="half">
                                            <span class="ttl">文件大小: </span>
                                            <span class="text">{{ core_item.file_size }}</span>
                                        </div>
                                    </div>
                                    <div class="list_row">
                                        <div class="half">
                                            <span class="ttl">MC版本: </span>
                                            <span class="text">{{ core_item.minecraft_version }}</span>
                                        </div><div class="half">
                                            <span class="ttl">文件版本: </span>
                                            <span class="default-text" v-if="core_item.core_version ==''">未知</span>
                                            <span class="text" v-else>{{ core_item.core_version }}</span>
                                        </div>
                                    </div>
                                    <div class="note" v-if="core_item.note === ''">
                                        (无备注)
                                    </div>
                                    <div class="note" v-else>
                                        {{ core_item.note }}
                                    </div>
                                </div>
                            </div>

                            <div class="add_button">
                                <button class="btn btn-primary btn-md" @click="add_serv_core"><i class="ion-plus-round"></i>&nbsp;&nbsp;&nbsp;添加核心</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <add-modal v-if="showAddModal" @close="showAddModal = false">
            <span slot="header">添加核心</span>
        </add-modal>

        <edit-modal v-if="showEditModal" @close="showEditModal = false">
            <span slot="header">编辑</span>
        </edit-modal>

        <del-modal v-if="showDeleteModal" @close="showDeleteModal = false">
            <span slot="header">删除</span>
        </del-modal>
    </section>
</template>

<script>
const LOADING = 0;
const ERROR   = 2;
const SUCCESS = 1;

import Loading from '../components/c-loading.vue';
import LoadError from '../components/c-error.vue';
import cModal from '../components/c-modal.vue';

export default {
    components: {
        'c-loading': Loading,
        'load-error': LoadError,
        'edit-modal': cModal,
        'del-modal': cModal,
        'add-modal': cModal
    },
    name : "ServerCore",
    data(){
        return {
            core_list : [],
            status: LOADING,
            showEditModal : false,
            showDeleteModal: false,
            showAddModal: false
        }
    },
    methods: {
        // fetch data from remote
        aj_load_core_list(){
            let app = this.$parent.$parent;
            app.ajax("GET",'/super_admin/api/get_core_file_info', this.init_core_list, this.on_load_error);
        },
        // click methods
        edit_serv_core(index){
            this.showEditModal = true;
        },

        delete_serv_core(index){
            this.showDeleteModal = true;
        },

        add_serv_core(){
            this.showAddModal = true;
        },
        // init list
        init_core_list(data){
            this.status = SUCCESS;
            this.core_list = data;
        },

        on_load_error(data){
            this.status = ERROR;
        },
    },
    mounted() {
        this.aj_load_core_list();
    }
}
</script>

<style>
div.core_nothing{
            text-align: center;
            font-size: 1.8rem;
            padding-top:4rem;
            color: #999;
        }

        div.add_button{
            margin-top:3rem;
            margin-bottom:3rem;
            text-align:center;
        }

        div.edit-button{
            position: absolute;
            right: 1rem;
            top: 0.75rem;
        }

        div.edit-button i{
            font-size: 1.6rem;
            color: gray;
        }

        div.edit-button a{
            margin-left:1rem;
            cursor: pointer;
        }

        div.core_list{
            border-bottom: 1px solid #dedede;
            min-height: 10.8rem;
            padding:1rem 0.5rem;
            position: relative;
        }

        div.core_list:hover{
            background-color: #f6f6f6;
        }
        div.core_list div.server_core_avatar{
            width: 6rem;
            height: 6rem;
            border: 1px solid #999;
            border-radius: 0.75rem;
            position: relative;
            float: left;
        }

        div.server_core_info{
            padding-left: 8rem;
            width: 100%;
        }

        div.server_core_info div.list_title{
            font-size:2rem;
            font-weight: bold;
            line-height: 1em;
            margin-bottom:0.7rem;
        }

        div.list_row{
            line-height: 1.4em;
            width: 100%;
        }
        div.list_row div.half{
            display: inline-block;
            width: 45%;
        }

        div.half span.ttl{
            margin-right: 0.5rem;
            display: inline-block;
        }
        div.note{
            width: 100%;
            color: #999;
        }

        span.default-text{
            color: #999;
        }
</style>
