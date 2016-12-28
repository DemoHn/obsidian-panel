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
                        <div v-if="core_list.length == 0">
                            <div class="core_nothing">这里空空如也 <br> 点击下面的「添加」按钮以添加核心</div>
                        </div>
                        <div class="core_list" v-for="core_item in core_list">
                            <div class="server_core_avatar">

                            </div>

                            <div class="server_core_info">
                                <div class="list_title">
                                    Torch-Project.jar
                                </div>
                                <div class="list_row">
                                    <div class="half">
                                        <span class="ttl">类型: </span>
                                        <span class="text">$2</span>
                                    </div>
                                    <div class="half">
                                        <span class="ttl">文件大小: </span>
                                        <span class="text">$2</span>
                                    </div>
                                    <div class="list_row">
                                        <div class="half">
                                            <span class="ttl">MC版本: </span>
                                            <span class="text">$2</span>
                                        </div>
                                        <div class="half">
                                            <span class="ttl">文件版本: </span>
                                            <span class="text">$2</span>
                                        </div>
                                    </div>
                                    <div class="note">
                                        暂无备注
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="add_button">
                                <button class="btn btn-primary btn-md"><i class="ion-plus-round"></i>&nbsp;&nbsp;&nbsp;添加核心</button>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </section>
</template>

<script>
    const LOADING = 0;
const ERROR   = 1;
const SUCCESS = 2;
export default {
    name : "ServerCore",
    data(){
        return {
            core_list : [2,3,4],
            state: LOADING
        }
    },
    methods: {

    },
    mounted() {

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

        div.core_list{
            border-bottom: 1px solid #dedede;
            min-height: 10.8rem;
            padding:1rem 0.5rem;
            position: relative;
        }

        div.core_list:hover{
            background-color: #f3f3f3;
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
            position: absolute;
            padding-left: 8rem;
            width: 100%;
        }

        div.server_core_info div.list_title{
            font-size:2rem;
            font-weight: bold;
            line-height: 1.3em;
        }

        div.list_row{
            line-height: 1.4em;
            width: 100%;
        }
        div.list_row div.half{
            position: relative;
            float: left;
            width: 45%;
        }

        div.half span.ttl{
            margin-right: 0.5rem;
            display: inline-block;
        }
        div.note{
            position: relative;
            float: left;
            width: 100%;
            color: #999;
        }
</style>
