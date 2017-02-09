<template lang="html">
    <div class="wrap">
        <div class="row" style="max-width: 1350px;">
            <div class="col-md-3" style="max-width: 24rem;">
                <div class="box box-default box-solid">
                    <div class="box-header with-border">
                        <h3 class="box-title" style="font-size: 16px;">编辑</h3>
                    </div>
                    <div class="box-body no-padding" style="display:block">
                        <div class="conf_category" :class="{selected: is_selected('general')}"><a @click="sel('general')">基本信息</a></div>
                        <div class="conf_category" :class="{selected: is_selected('core')}"><a @click="sel('core')">核心及Java版本</a></div>
                        <div class="conf_category" :class="{selected: is_selected('properties')}"><a @click="sel('properties')">游戏属性</a></div>
                        <div class="conf_category" :class="{selected: is_selected('info')}"><a @click="sel('info')">服务器信息</a></div>
                        <div class="conf_category" :class="{selected: is_selected('ftp')}"><a @click="sel('ftp')">FTP设置</a></div>
                        <div class="conf_category" :class="{selected: is_selected('delete')}"><a @click="sel('delete')">删除服务器</a></div>
                    </div>
                </div>
            </div>
            <!-- general -->
            <div class="col-md-5">
                <div class="box box-solid">
                    <div class="box-body">
                        <edit-item>
                            <span slot="title">世界名称</span>
                            <div slot="description">此项仅表示为面板里的「世界名称」。</div>
                            <div slot="body">
                                <input name="" type="text" value="" class="form-control input-text" />
                                <button class="btn btn-default btn-v">保存</button>
                            </div>
                        </edit-item>
                        <edit-item>
                            <span slot="title">侦听端口</span>
                            <div slot="description">设置服务器侦听端口。重启后方能生效。</div>
                            <div slot="body">
                                <input name="" type="number" value="" class="form-control input-text" />
                                <button class="btn btn-default btn-v">保存</button>
                            </div>
                        </edit-item>
                        <edit-item>
                            <span slot="title">最大玩家数</span>
                            <div slot="description">可同时登录此服务器的最大用户数目。</div>
                            <div slot="body">
                                <input name="" type="number" value="" class="form-control input-text" />
                                <button class="btn btn-default btn-v">保存</button>
                            </div>
                        </edit-item>
                        <edit-item>
                            <span slot="title">最大运行内存</span>
                            <div slot="description">可以分配给此服务器的最大内存，以GB为单位。「亦即java的 -Xmx 参数」</div>
                            <div slot="body">
                                <input name="" type="number" value="" class="form-control input-text" />
                                <span style="margin-right: 1rem;">G</span>
                                <button class="btn btn-default btn-v">保存</button>
                            </div>
                        </edit-item>
                    </div>
                </div>

                <!-- core -->
            </div>
        </div>
    </div>
</template>

<script>
import WebSocket from "../../lib/websocket";
import EditInstanceItem from "../../components/edit_instance/edit-item.vue"

export default {
    components:{
        "edit-item" : EditInstanceItem
    },
    data(){
        return {
            'sel_val' : 'general'
        }
    },
    methods:{
        is_selected(item){
            if(item == this.sel_val){
                return true;
            }else{
                return false;
            }
        },
        sel(item){
            this.sel_val = item;
        }
    },
    mounted(){
        console.log(this.$route.params.id);
    }
}
</script>

<style>
div.wrap{
    padding-top: 2rem;
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

div.conf_category.selected{
    border-left: 3px solid orange;
    font-weight: bold;
}

input.input-text[type=text]{
    max-width: 20rem;
    display: inline-block;
    margin-right: 1rem;
}

input.input-text[type=number]{
    max-width: 10rem;
    display: inline-block;
    margin-right: 1rem;
}

div.conf_category a{
    color: #333;
}

div.conf_category a:hover{
    text-decoration: underline;
}

.btn-v{
    vertical-align: top !important;
}
</style>
