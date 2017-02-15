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
            <div class="col-md-5" v-show="sel_val == 'general'">
                <div class="box box-solid">
                    <div class="box-body">
                        <edit-item :JR_status="s_world_name">
                            <span slot="title">世界名称</span>
                            <div slot="description">此项仅表示为面板里的「世界名称」。</div>
                            <div slot="body">
                                <input type="text" v-model="world_name" class="form-control input-text" />
                                <button class="btn btn-default btn-v" :disabled="!changed_from_initial('world_name')" @click="edit_config('world_name')">保存</button>
                            </div>
                        </edit-item>
                        <edit-item :JR_status="s_listen_port">
                            <span slot="title">侦听端口</span>
                            <div slot="description">设置服务器侦听端口。重启服务器方能生效。</div>
                            <div slot="body">
                                <input v-model="listen_port" type="number" class="form-control input-text" />
                                <button class="btn btn-default btn-v" :disabled="!changed_from_initial('listen_port')" @click="edit_config('listen_port')">保存</button>
                            </div>
                        </edit-item>
                        <edit-item :JR_status="s_number_players">
                            <span slot="title">最大玩家数</span>
                            <div slot="description">可同时登录此服务器的最大用户数目。重启服务器方能生效。</div>
                            <div slot="body">
                                <input v-model="number_players" type="number" class="form-control input-text" />
                                <button class="btn btn-default btn-v" :disabled="!changed_from_initial('number_players')" @click="edit_config('number_players')">保存</button>
                            </div>
                        </edit-item>
                        <edit-item :JR_status="s_number_RAM">
                            <span slot="title">最大运行内存</span>
                            <div slot="description">可以分配给此服务器的最大内存，以GB为单位。亦即java的 -Xmx 参数。重启服务器方能生效。</div>
                            <div slot="body">
                                <input v-model="number_RAM" type="number" class="form-control input-text" />
                                <span style="margin-right: 1rem;">G</span>
                                <button class="btn btn-default btn-v" :disabled="!changed_from_initial('number_RAM')" @click="edit_config('number_RAM')" >保存</button>
                            </div>
                        </edit-item>
                    </div>
                </div>
            </div>
            <!-- core -->
            <div class="col-md-5" v-show="sel_val == 'core'">
                <div class="box box-solid">
                    <div class="box-body">
                        <edit-item>
                            <span slot="title">服务器核心</span>
                            <div slot="description">选择用于启动服务器的核心。如果服务器已经运行，不建议随意更换。重启服务器方能生效。</div>
                            <div slot="body">
                                <select name="core_file_id" class="form-control" v-model="core_file_id" >
                                    <option :value="null" v-if="server_cores_list.length === 0">-- 还没有选择 --</option>
                                    <option :value="item['index']" v-for="item in server_cores_list">{{ item['name'] }}</option>
                                </select>
                            </div>
                        </edit-item>
                        <edit-item>
                            <span slot="title">Java版本</span>
                            <div slot="description">用于启动此服务器的java之版本。推荐选择Java8。重启服务器方能生效。</div>
                            <div slot="body">
                                <select class="form-control" v-model="java_bin_id">
                                    <option :value="null" v-if="java_versions_list.length === 0">-- 还没有选择 --</option>
                                    <option :value="item['index']" v-for="item in java_versions_list">{{ item['name'] }}</option>
                                </select>
                            </div>
                        </edit-item>
                    </div>
                </div>
            </div>

            <!-- properties -->
            <div class="col-md-6" v-show="sel_val == 'properties'">
                <div class="box box-solid">
                    <div class="box-body">
                         <edit-item>
                             <span slot="title">游戏属性</span>
                             <div slot="description">设置游戏内属性。其他属性可以到server.properties文件中修改。</div>
                             <div slot="body">
                                 <div class="row">
                                     <div class="col-md-6">
                                         <div class="setting-item"><span class="item-text"><i class="red-star"></i>正版验证</span>
                                             <span class="input-element">
                                                 <select name="online-mode" class="form-control" v-model="s_online_mode">
                                                     <option :value="'true'">开启</option>
                                                     <option :value="'false'">关闭</option>
                                                 </select>
                                             </span>
                                         </div>

                                         <div class="setting-item"><span class="item-text">PVP模式</span>
                                             <span class="input-element">
                                                 <select  class="form-control" v-model="s_pvp">
                                                     <option :value="'true'">开启</option>
                                                     <option :value="'false'">关闭</option>
                                                 </select>
                                             </span>
                                         </div>

                                         <div class="setting-item"><span class="item-text">游戏难度</span>
                                             <span class="input-element">
                                                 <select  class="form-control" v-model="s_difficulty">
                                                     <option :value="0">0</option>
                                                     <option :value="1">1</option>
                                                     <option :value="2">2</option>
                                                     <option :value="3">3</option>
                                                 </select>
                                             </span>
                                         </div>

                                         <div class="setting-item"><span class="item-text">游戏模式</span>
                                             <span class="input-element">
                                                 <select  class="form-control" v-model="s_gamemode">
                                                     <option :value="0">0</option>
                                                     <option :value="1">1</option>
                                                     <option :value="2">2</option>
                                                 </select>
                                             </span>
                                         </div>

                                         <div class="setting-item"><span class="item-text">怪物生成</span>
                                             <span class="input-element">
                                                 <select class="form-control" v-model="s_spawn_monsters">
                                                     <option :value="'true'">开启</option>
                                                     <option :value="'false'">关闭</option>
                                                 </select>
                                             </span>
                                         </div>

                                         <div class="setting-item"><span class="item-text">生成下界</span>
                                             <span class="input-element">
                                                 <select class="form-control" v-model="s_allow_nether">
                                                     <option :value="'true'">开启</option>
                                                     <option :value="'false'">关闭</option>
                                                 </select>
                                             </span>
                                         </div>

                                     </div>
                                     <div class="col-md-6" style="margin-left: -5rem;">
                                         <div class="setting-item"><span class="item-text">世界种子</span>
                                             <span class="input-element">
                                                 <input class="form-control w-input" type="text" />
                                             </span>
                                         </div>
                                         <div class="setting-item"><span class="item-text">最大建筑高度</span>
                                             <span class="input-element">
                                                 <input class="form-control w-input" type="text" />
                                             </span>
                                         </div>
                                         <div class="setting-item"><span class="item-text">命令方块</span>
                                             <span class="input-element">
                                                 <select class="form-control" v-model="s_allow_nether">
                                                     <option :value="'true'">开启</option>
                                                     <option :value="'false'">关闭</option>
                                                 </select>
                                             </span>
                                         </div>
                                         <div class="setting-item"><span class="item-text">生成NPC</span>
                                             <span class="input-element">
                                                 <select class="form-control" v-model="s_allow_nether">
                                                     <option :value="'true'">开启</option>
                                                     <option :value="'false'">关闭</option>
                                                 </select>
                                             </span>
                                         </div>
                                         <div class="setting-item"><span class="item-text">生成动物</span>
                                             <span class="input-element">
                                                 <select class="form-control" v-model="s_allow_nether">
                                                     <option :value="'true'">开启</option>
                                                     <option :value="'false'">关闭</option>
                                                 </select>
                                             </span>
                                         </div>
                                         <div class="setting-item"><span class="item-text">锁定游戏模式</span>
                                             <span class="input-element">
                                                 <select class="form-control" v-model="s_allow_nether">
                                                     <option :value="'true'">开启</option>
                                                     <option :value="'false'">关闭</option>
                                                 </select>
                                             </span>
                                         </div>
                                     </div>

                                 </div>
                                 <div>
                                     <button class="btn btn-default btn-v">保存</button>
                                 </div>
                             </div>
                         </edit-item>
                    </div>
                </div>
            </div>

            <!-- info -->
            <div class="col-md-5" v-show="sel_val == 'info'">
                <div class="box box-solid">
                    <div class="box-body">
                        <edit-item>
                            <span slot="title">LOGO</span>
                            <div slot="description">服务器的LOGO。要求为64x64像素的PNG图像。</div>
                            <div slot="body">
                                <logo-uploader ref="LOGO"></logo-uploader>
                            </div>
                        </edit-item>
                        <edit-item>
                            <span slot="title">每日讯息</span>
                            <div slot="description">服务器在MC客户端中的提示语。亦即motd。</div>
                            <div slot="body">
                                233
                            </div>
                        </edit-item>
                    </div>
                </div>
            </div>

            <!-- core -->
            <div class="col-md-5" v-show="sel_val == 'ftp'">
                <div class="box box-solid">
                    <div class="box-body">
                        <edit-item>
                            <span slot="title">FTP账户</span>
                            <div slot="description"></div>
                            <div slot="body">
                                <input name="" type="number" value="" class="form-control input-text" />
                                <button class="btn btn-default btn-v">保存</button>
                            </div>
                        </edit-item>
                        <edit-item>
                            <span slot="title">FTP密码</span>
                            <div slot="description"></div>
                            <div slot="body">
                                <input name="" type="number" value="" class="form-control input-text" />
                                <button class="btn btn-default btn-v">保存</button>
                            </div>
                        </edit-item>
                    </div>
                </div>
            </div>

            <!-- core -->
            <div class="col-md-5" v-show="sel_val == 'delete'">
                <div class="box box-solid">
                    <div class="box-body">
                        TODO
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import WebSocket from "../../lib/websocket";
import EditInstanceItem from "../../components/edit_instance/edit-item.vue"
import LogoUploader from "../../components/new_instance/logo-uploader.vue"

let deepcopy = require("deepcopy");
let ws       = new WebSocket();

export default {
    components:{
        "edit-item" : EditInstanceItem,
        "logo-uploader" : LogoUploader
    },
    data(){
        let assert_keys = ["world_name", "number_RAM", "listen_port", "core_file_id", "java_bin_id", "server_properties", "ftp_account_name", "default_ftp_password", "number_players"];
        let dt = {
            'sel_val' : 'general',
            'inst_id' : this.$route.params.id,
            'init_conf' : {},

            // core & java version
            "server_cores_list" : [],
            "java_versions_list" : [],

            // server properties
            "server_properties" : {},
        }
        // append assert keys
        for(var i=0;i<assert_keys.length;i++){
            let key = assert_keys[i];
            dt[key] = "";
            // assert hint (tick or cross or loading icon)
            dt["s_" + key] = null;
        }

        return dt;
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
        },

        changed_from_initial(item){
            if(this[item] == null){
                return true;
            }else{
                if(this[item] == this["init_conf"][item] || this[item] == ""){
                    return false;
                }else{
                    return true;
                }
            }
        },

        edit_config(item){
            let payload = {
                "key" : item,
                "value" : this[item]
            };

            this["s_" + item ] = 0; //loading state 
            ws.ajax("POST", "/server_inst/edit_inst/" + this.inst_id + "/edit_config", payload, (msg)=>{
                this["s_" + item ] = 2; //success
            },(code)=>{
                this["s_" + item ] = 1; //fail
            })
        },
        aj_get_init_data(callback){
            ws.ajax("GET", "/server_inst/edit_inst/" + this.inst_id + "/init_edit_data", (msg)=>{
                if(typeof(callback) === "function"){
                    callback(msg);
                }
            })
        }
    },
    mounted(){
        let v = this;
        this.aj_get_init_data((msg)=>{
            v.init_conf = deepcopy(msg);
            for(let item in msg){
                v[item] = msg[item];
            }
        });
    }
}
</script>

<style scoped>
select{
    max-width: 80% !important;
    margin-bottom: 0 !important;
}

input.w-input{
    width: 80% !important;
}

div.setting-item{
    width:100%;
    min-height: 6rem !important;
    padding: 0.5rem 2rem 0.5rem 0 !important;
    display: inline-block;
}

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

div.setting-item span.item-text{
    width: 40%;
    float:left;
    height:100%;
    display: inline-block;
    text-align: center;
    line-height: 2.5em;
}
</style>
