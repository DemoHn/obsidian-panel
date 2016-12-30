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
                                            <span class="default-text" v-if="core_item.core_type == 'other'">其他</span>
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

        <!-- add core file-->
        <add-modal v-if="showAddModal" @cancel="showAddModal = false">
            <span slot="header">添加核心</span>
        </add-modal>

        <!-- edit core file -->
        <edit-modal v-if="showEditModal" @cancel="showEditModal = false" @confirm="confirm_edit">
            <span slot="header">编辑</span>
            <div slot="body" class="edit_model_content">
                <div class="form_group">
                    <div class="form_label">
                        文件名：
                    </div>
                    <div class="form_input">
                        <input type="text" class="form-control" v-model="edit_form.file_name"/>
                    </div>
                </div>
                <div class="form_group">
                    <div class="form_label">
                        类型：
                    </div>
                    <div class="form_input">
                        <select name="" class="form-control" v-model="edit_form.core_type">
                            <option :value="'bukkit'">Bukkit</option>
                            <option :value="'spigot'">Spigot</option>
                            <option :value="'vanilla'">Vanilla</option>
                            <option :value="'forge'">Forge</option>
                            <option :value="'mcpc'">MCPC+</option>
                            <option :value="'kcauldron'">KCauldron</option>
                            <option :value="'thermos'">Thermos</option>
                            <option :value="'torch'">Torch</option>
                            <option :value="'other'">其他</option>
                        </select>
                    </div>
                </div>
                <div class="form_group">
                    <div class="form_label">MC版本：</div>
                    <div class="form_input">
                        <input type="text" class="form-control" v-model="edit_form.minecraft_version"/>
                    </div>
                </div>
                <div class="form_group">
                    <div class="form_label">
                        文件版本：
                    </div>
                    <div class="form_input">
                        <input type="text" class="form-control" v-model="edit_form.core_version"/>
                    </div>
                </div>
                <div class="form_group">
                    <div class="form_label">
                        备注：
                    </div>
                    <div class="form_input">
                        <textarea class="form-control" v-model="edit_form.note"></textarea>
                    </div>
                </div>
                <div class="error-hint" v-show="edit_modal_error">
                    编辑失败，请重试
                </div>
            </div>
        </edit-modal>

        <!-- delete confrim prompt -->
        <del-modal v-if="showDeleteModal" @cancel="showDeleteModal = false" @confirm="confirm_delete">
            <span slot="header">删除</span>
            <div slot="body">
                确认删除「 <b>{{ delete_file_name }}</b> 」？此操作将不可逆，及可能影响以此为核心的服务器！
                <div class="error-hint" v-show="delete_modal_error">
                    删除失败，请重试
                </div>
            </div>
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
            edit_form:{
                file_name: "",
                core_type: 'vanilla',
                minecraft_version: "",
                core_version: "",
                note: ""
            },
            showEditModal : false,
            _edit_index: null,
            edit_modal_error: false,
            // delete modal
            showDeleteModal: false,
            _delete_index: null,
            delete_file_name: null,
            delete_modal_error: false,

            // add modal
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
            this.edit_form["file_name"] = this.core_list[index]["file_name"];
            this.edit_form["core_type"] = this.core_list[index]["core_type"];
            this.edit_form["minecraft_version"] = this.core_list[index]["minecraft_version"];
            this.edit_form["core_version"] = this.core_list[index]["core_version"];
            this.edit_form["note"] = this.core_list[index]["note"];
            // init modal params
            this.showEditModal = true;
            this._edit_index = index;
            this.edit_modal_error = false;
        },
        // on confirm
        confirm_edit(){
            let app = this.$parent.$parent;
            const ajax_data = {
                "file_name" : this.edit_form.file_name,
                "file_version" : this.edit_form.core_version,
                "description" : this.edit_form.note,
                "core_type" : this.edit_form.core_type,
                "mc_version" : this.edit_form.minecraft_version
            }

            let _index = this._edit_index;
            let core_file_id = this.core_list[_index]["core_id"];
            let v = this;
            app.ajax("POST", "/super_admin/api/edit_core_file_params/"+core_file_id, ajax_data, (msg)=>{
                for(let key in v.edit_form)
                    v.core_list[_index][key] = v.edit_form[key];
                v.showEditModal = false;
                v.edit_modal_error = false;
            },(code)=>{
                v.edit_modal_error = true;
            })
        },

        delete_serv_core(index){
            this.showDeleteModal = true;
            this._delete_index = index;
            this.delete_modal_error = false;
            this.delete_file_name = this.core_list[index]["file_name"];
        },

        confirm_delete(){
            let app = this.$parent.$parent;
            let _index = this._delete_index;
            let core_file_id = this.core_list[_index]["core_id"];
            let v = this;
            app.ajax("GET", "/super_admin/api/delete_core_file/"+core_file_id, (msg)=>{
                // on success
                v.showDeleteModal = false;
                v.core_list.splice(_index, 1);
                v.delete_modal_error = false;
            },(code)=>{
                // on error
                v.delete_modal_error = true;
            })
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

        input.form-control,
        select.form-control{
            width: 75%;
        }

        div.form_input textarea{
            width: 75%;
            height: 8rem;
        }

        div.edit_model_content div.form_group{
            line-height: 2em;
            font-size: 1.5rem;
            margin-top: 1.2rem;
            margin-bottom: 1.2rem;
        }

        div.edit_model_content div.form_label{
            position: relative;
            float:left;
            min-width: 8rem;
            width: 25%;
        }

        div.edit_model_content div.form_input{
            width: 100%;
            padding-left: 25%;
        }

        div.error-hint{
            font-size: 1.25rem;
            text-align: right;
            color: red;
        }
</style>
