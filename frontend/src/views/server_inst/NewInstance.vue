<template lang="html">
    <div class="main-frame">
        <ul class="timeline">

            <!-- timeline time label -->
            <li class="time-label">
                <span class="bg-red">
                    BASIC SETTING
                </span>
            </li>
            <!-- /.timeline-label -->

            <!-- timeline item -->
            <!-- world name-->
            <inst-item input_placeholder="在此处输入世界名称" :model="world_name" :JR_result="world_name_assert">
                <span slot="title">世界名称</span>
                <!--<div slot="control"></div>-->
                <div slot="description"></div>
                <div slot="error-msg">世界名不得为空，或不得重名！</div>
            </inst-item>

            <!-- listening port-->
            <inst-item input_placeholder="1~65535" :model="listen_port" :JR_result="port_assert">
                <span slot="title">侦听端口</span>
                <div slot="description"></div>
                <div slot="error-msg">端口须在1-65535之间</div>
            </inst-item>

            <!-- max players -->
            <inst-item>
                <span slot="title">玩家上限</span>
                <div slot="control">
                    <div>
                    <span class="input-element">
                        <input type="range" min="1" max="10" step="1" list="tickmarks" v-model="range_players">
                        <datalist id="tickmarks">
                            <option>1</option>
                            <option>2</option>
                            <option>3</option>
                            <option>4</option>
                            <option>5</option>
                            <option>6</option>
                            <option>7</option>
                            <option>8</option>
                            <option>9</option>
                            <option>10</option>
                        </datalist>
                        <input type="number" name="max_user" v-model="number_players">
                    </span>
                    </div>
                </div>
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>
            <!-- max RAM -->
            <inst-item>
                <span slot="title">内存上限</span>
                <div slot="control">
                    <div>
                        <span class="input-element">
                            <input type="range" min="1" max="6" step="1" list="RAMs" v-model="range_RAM">
                            <datalist id="RAMs">
                                <option>1</option>
                                <option>2</option>
                                <option>3</option>
                                <option>4</option>
                                <option>5</option>
                                <option>6</option>
                            </datalist>
                            <input type="number" name="max_RAM" style="width:18%" v-model="number_RAM" >&nbsp;&nbsp;<span>G</span>
                        </span>
                    </div>
                </div>
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>
            <!-- server core -->
            <inst-item>
                <span slot="title">服务器核心</span>
                <div slot="control">
                    <div>
                         <span class="input-element">
                             <select name="core_file_id" class="form-control" v-model="core_file_id" >
                                 <option :value="null" v-if="server_cores_list.length === 0">-- 还没有选择 --</option>
                                 <option :value="item['index']" v-for="item in server_cores_list">{{ item['name'] }}</option>
                             </select>&nbsp;&nbsp;&nbsp;<a href="/super_admin/server_core" target="_blank">添加核心</a>
                         </span>
                    </div>
                </div>
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>

            <!-- java version -->
            <inst-item>
                <span slot="title">Java 版本</span>
                <div slot="control">
                    <div>
                         <span class="input-element">
                             <select class="form-control" v-model="java_bin_id">
                                 <option :value="null" v-if="java_versions_list.length === 0">-- 还没有选择 --</option>
                                 <option :value="item['index']" v-for="item in java_versions_list">{{ item['name'] }}</option>
                             </select>&nbsp;&nbsp;&nbsp;<a href="/super_admin/java_binary" target="_blank">添加Java版本</a>
                         </span>
                    </div>
                </div>
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>

            <li class="time-label">
                <span class="bg-red">
                    BASIC SETTING
                </span>
            </li>
            <!-- server properties-->
            <inst-item required="false">
                <span slot="title">世界属性</span>
                <div slot="control">
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
                    <div class="setting-item">
                        <span class="des">注： 其他配置可在 server.properties 文件中修改。</span>
                    </div>
                </div>
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>

            <li class="time-label">
                <span class="bg-red">
                    BASIC SETTING
                </span>
            </li>

            <inst-item>
                <span slot="title">LOGO</span>
                <div slot="control">
                    <logo-uploader></logo-uploader>
                </div>
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>

            <inst-item>
                <span slot="title">每日讯息</span>
                <div slot="control">
                    <motd-editor></motd-editor>
                </div>
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>

            <inst-item>
                <span slot="title">FTP 账户</span>
                <!--<div slot="control"></div>-->
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>

            <inst-item>
                <span slot="title">FTP 密码</span>
                <!--<div slot="control"></div>-->
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>
        </ul>
    </div>
</template>

<script>
    import InstanceItem from "../../components/new_instance/inst-item.vue"
    import LogoUploader from "../../components/new_instance/logo-uploader.vue"
    import MotdEditor from "../../components/new_instance/motd-editor.vue"
    import WebSocket from "../../lib/websocket.js"
    export default {
        components:{
            "inst-item" : InstanceItem,
            'logo-uploader': LogoUploader,
            'motd-editor' : MotdEditor
        },
        name:"NewInstnace",
        data(){
            return {
                /*basic config*/
                "range_players" : 1,
                "number_players" : 10,
                "range_RAM" : 1,
                "number_RAM" : 1,
                "listen_port" : 0,
                "world_name" : "",
                "core_file_id" : null,
                "java_bin_id" : null,

                /*asserts*/
                "world_name_assert" : null,
                "port_assert": null,
                "ftp_account_assert" : null,

                /*load from ajax*/
                "server_cores_list" : [],
                "java_versions_list" : [],
                "ftp_account_name" : null,
                /*miscellaneous*/
                "default_ftp_password" : true,

                /*server properties*/
                "server_properties" : "{}",
                "s_online_mode" : "true",
                "s_pvp" : "true",
                "s_difficulty" : 1,
                "s_spawn_monsters" : "true",
                "s_allow_nether" : "true",
            }
        },
        methods:{
            aj_get_lists(){
                let ws = new WebSocket();
                ws.ajax("GET","/server_inst/api/new_inst", (msg)=>{
                    this.server_cores_list = msg.server_cores;
                    this.java_versions_list = msg.java_versions;
                    this.ftp_account_name = msg.FTP_account_name;

                    if(this.server_cores_list.length > 0){
                        this.core_file_id = this.server_cores_list[0]['index'];
                    }

                    if(this.java_versions_list.length > 0){
                        this.java_bin_id = this.java_versions_list[0]['index'];
                    }
                },(msg)=>{

                });
            }
        },
        mounted(){
            this.aj_get_lists();
        }
    }
</script>

<style>
div.main-frame{
    max-width: 1080px;
    padding-top: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
    height: 100%;
}

span.input-element{
    width: 100%;
    height:100%;
    vertical-align: text-top;
    display: inline-block;
}

span.input-element input[type="range"]{
    display: inline-block;
    width: 60%;
    line-height: 3em;
    margin-right:4%;
    vertical-align: middle;
}

span.input-element select{
    display: inline-block;
    width: 60%;
}

span.input-element input[type="text"],
span.input-element input[type="password"]{
    width: 60%;
    display: inline-block;
}

span.input-element input[type="number"]{
    display: inline-block;
    width: 24%;
    line-height: 2em;
    vertical-align: middle;
}

div.box-body div.setting-item{
    width:100%;
    min-height: 4.5em;
    padding: 1em 2em 1em 0;
    display: inline-block;
}

div.max-width-limit{
    max-width: 560px;
}
div.margin-s{
    padding-top:1em;
    padding-bottom:1em;
}
div.setting-item span.item-text{
    position:relative;
    width: 30%;
    float:left;
    height:100%;
    display: inline-block;
    text-align: center;
    line-height: 2em;
}

div.setting-item span.input-element{
    width: 60%;
    height:100%;
    vertical-align: text-top;
    display: inline-block;
}

div.setting-item span.input-element select{
    width: 80%;
    margin-bottom: 2rem;
}

span.des{
    margin-left:2em;
    color: #666666;
}

@media(max-width: 766px){
    div.main-frame{
        padding-top: 2rem;
    }
}
</style>
