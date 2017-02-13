<template lang="html">
    <div class="main-frame">
        <ul class="timeline">

            <!-- timeline time label -->
            <li class="time-label">
                <span class="bg-green">
                    &nbsp;&nbsp;基本设置&nbsp;&nbsp;
                </span>
            </li>
            <!-- /.timeline-label -->

            <!-- timeline item -->
            <!-- world name-->
            <inst-item :JR_result="world_name_assert">
                <span slot="title">世界名称</span>
                <div slot="control">
                    <input type="text" placeholder="在此处输入世界名称" @focus="clear_assert('inst_name')" @blur="set_assert('inst_name')" v-model="world_name"/>
                </div>
                <div slot="description"></div>
                <div slot="error-msg">世界名不得为空，或不得重名！</div>
            </inst-item>

            <!-- listening port-->
            <inst-item :JR_result="port_assert">
                <span slot="title">侦听端口</span>
                <div slot="control">
                       <input type="text" placeholder="1~65535" @focus="clear_assert('port')" @blur="set_assert('port')" v-model="listen_port" />
                </div>
                <div slot="description"></div>
                <div slot="error-msg">端口须为1-65535之间之数字，且不得重复</div>
            </inst-item>

            <!-- max players -->
            <inst-item :JR_result="max_player_assert">
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
            <inst-item :JR_result="max_RAM_assert">
                <span slot="title">内存上限</span>
                <div slot="control">
                    <div>
                        <span class="input-element">
                            <input type="range" min="1" max="8" step="1" list="RAMs" v-model="range_RAM">
                            <datalist id="RAMs">
                                <option>1</option>
                                <option>2</option>
                                <option>3</option>
                                <option>4</option>
                                <option>5</option>
                                <option>6</option>
                                <option>7</option>
                                <option>8</option>
                            </datalist>
                            <input type="number" name="max_RAM" style="width:18%" v-model="number_RAM" >&nbsp;&nbsp;<span>G</span>
                        </span>
                    </div>
                </div>
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>
            <!-- server core -->
            <inst-item :JR_result="server_core_assert">
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
                <div slot="error-msg">请至少选择一个核心!!</div>
            </inst-item>

            <!-- java version -->
            <inst-item :JR_result="java_version_assert">
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
                <div slot="error-msg">请至少选择一个Java版本!!</div>
            </inst-item>

            <li class="time-label">
                <span class="bg-blue">
                    &nbsp;&nbsp;世界属性&nbsp;&nbsp;
                </span>
            </li>
            <!-- server properties-->
            <inst-item :required="false" :JR_result="server_properties_assert">
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
                    <div class="setting-item">
                        <span class="des">注： 其他配置可在 server.properties 文件中修改。</span>
                    </div>
                </div>
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>

            <li class="time-label">
                <span class="bg-green">
                    &nbsp;&nbsp;杂项&nbsp;&nbsp;
                </span>
            </li>

            <inst-item :required="false" :JR_result="server_logo_assert">
                <span slot="title">LOGO</span>
                <div slot="control">
                    <logo-uploader ref="LOGO"></logo-uploader>
                </div>
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>

            <inst-item :required="false" :JR_result="motd_assert">
                <span slot="title">每日讯息</span>
                <div slot="control">
                    <motd-editor ref="motdEditor"></motd-editor>
                </div>
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>

            <inst-item :JR_result="ftp_account_assert">
                <span slot="title">FTP 账户</span>
                <div slot="control">
                    <input type="text" placeholder="FTP账户" @focus="clear_assert('ftp_account')" @blur="set_assert('ftp_account')" v-model="ftp_account_name"/>
                </div>
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>

            <inst-item :JR_result="ftp_password_assert">
                <span slot="title">FTP 密码</span>
                <div slot="control">
                    <span class="input-element">
                        <div class="mask" v-show="default_ftp_password">
                            <span class="mask-text">&lt;与登录密码相同&gt;</span>
                        </div>
                        <input type="password" name="ftp_password" v-model="ftp_password" class="form-control" :disabled="default_ftp_password" style="width: 60%;border: 1px solid #666 !important;">&nbsp;&nbsp;
                        <span>
                            <a v-if="default_ftp_password" @click="default_ftp_password = false;">自定义密码</a>
                            <a v-if="!default_ftp_password" @click="default_ftp_password = true;">使用登录密码</a>
                        </span>
                    </span>
                </div>
                <div slot="description"></div>
                <div slot="error-msg"></div>
            </inst-item>

            <li>
                <div class="col-md-5 timeline-item">
                    <button class="finish_btn" v-if="button_status === 0" @click="clk_create_instance">一切准备就绪，开始创建！</button>
                    <button class="finish_btn" v-else-if="button_status === 1" disabled><i class="fa fa-circle-o-notch fa-spin fa-fw"></i>&nbsp;&nbsp;&nbsp;正在检查配置...</button>
                    <button class="finish_btn" v-if="button_status === 2" @click="clk_create_instance">参数有错误，请修改后重试！</button>
            </li>
        </ul>

    </div>
</template>

<script>
    import InstanceItem from "../../components/new_instance/inst-item.vue"
    import LogoUploader from "../../components/new_instance/logo-uploader.vue"
    import MotdEditor from "../../components/new_instance/motd-editor.vue"
    import WebSocket from "../../lib/websocket.js"
    import VueRouter from 'vue-router'
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
                "max_player_assert" : null,
                "max_RAM_assert" : null,
                "server_core_assert" : null,
                "java_version_assert" : null,
                "server_properties_assert" : null,
                "server_logo_assert" : null,
                "motd_assert" : null,
                "ftp_account_assert" : true,
                "ftp_password_assert" : null,

                /*load from ajax*/
                "server_cores_list" : [],
                "java_versions_list" : [],
                "ftp_account_name" : null,
                /*miscellaneous*/
                "default_ftp_password" : true,
                "ftp_password" : "",

                /*server properties*/
                "server_properties" : "{}",
                "s_online_mode" : "true",
                "s_pvp" : "true",
                "s_difficulty" : 1,
                "s_spawn_monsters" : "true",
                "s_allow_nether" : "true",
                "s_gamemode" : 0,
                /*button*/
                "button_status" : 0
            }
        },
        computed:{
            server_properties(){
                let json_data = {
                    "online-mode" : this.s_online_mode,
                    "pvp": this.s_pvp,
                    "difficulty" : this.s_difficulty,
                    "spawn-monsters": this.s_spawn_monsters,
                    "allow-nether": this.s_allow_nether,
                    "gamemode" : this.s_gamemode
                }
                return JSON.stringify(json_data);
            }
        },
        methods:{
            clear_assert(){

            },
            set_assert(type){
                let v =this;
                if(type === "port"){
                    this.aj_assert(type, v.listen_port, (msg)=>{
                        v.port_assert = msg;
                    })
                }else if(type == "inst_name"){
                    this.aj_assert(type, v.world_name, (msg)=>{
                        v.world_name_assert = msg;
                    })
                }else if(type == "ftp_account"){
                    this.aj_assert(type, v.ftp_account_name, (msg)=>{
                        v.ftp_account_assert = msg;
                    })
                }
            },

            clk_create_instance(){
                let asserts_data = true;
                this.button_status = 1;

                let ws = new WebSocket();
                
                // start to check config
                // auto pass
                this.max_player_assert = true;
                this.max_RAM_assert = true;
                this.server_properties_assert = true;
                this.server_logo_assert = true;
                this.motd_assert = true;
                this.ftp_password_assert = true;

                // check value, and judge
                if(this.core_file_id == null){
                    asserts_data = false;
                    this.server_core_assert = false;
                    this.button_status = 0;
                    return ;
                }else{
                    this.server_core_assert = true;
                }

                if(this.java_bin_id == null){
                    asserts_data = false;
                    this.java_version_assert = false;
                    this.button_status = 0;
                    return ;
                }else{
                    this.java_version_assert = true;
                }

                // assert data by ajax
                let _assert_data = this.listen_port + "," + this.world_name + "," + this.ftp_account_name;
                let v= this;
                ws.ajax("GET", "/server_inst/api/new_inst/assert_input?type=_all&data="+_assert_data, (msg)=>{
                    v.world_name_assert = msg["inst_name"];
                    v.port_assert = msg["port"];
                    v.ftp_account_assert = msg["ftp_account"];

                    if( !(msg["inst_name"] && msg["port"] && msg["ftp_account"]) ){
                        asserts_data = false;
                    }

                    // finally , send request if everything is OK
                    if(asserts_data === true){
                        v.aj_create_inst();
                        return ;
                    }else{
                        v.button_status = 2;
                    }

                },(code)=>{
                    this.button_status = 2;
                })
            },
            aj_create_inst(){
                let ws = new WebSocket();
                let that = this;

                let logo_full_url = this.$refs.LOGO.getImageURL();
                let logo_url_arr  = logo_full_url.split("/");
                let logo_url      = logo_url_arr[logo_url_arr.length-1];

                let creat_data = {
                    "inst_name" : that.world_name,
                    "core_file_id" : that.core_file_id,
                    "java_bin_id" : that.java_bin_id,
                    "listening_port" : that.listen_port,
                    "max_RAM" : parseInt(that.number_RAM),
                    "max_user" : parseInt(that.number_players),
                    "server_properties" : that.server_properties,
                    "logo_url" : logo_url,
                    "motd" : this.$refs.motdEditor.parse(),
                    "ftp_account" : that.ftp_account_name,
                    "ftp_default_password" : that.default_ftp_password,
                    "ftp_password" : that.ftp_password
                }

                ws.ajax("POST", "/server_inst/api/new_inst", creat_data, (msg)=>{
                    let inst_id = msg;
                    location.href = "/server_inst/dashboard#" + inst_id;
                })
                return ;
            },
            // ajax function , prefix wih "aj"
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
            },
            aj_assert(type, data, success_callback){
                let ws = new WebSocket();
                ws.ajax("GET", "/server_inst/api/new_inst/assert_input?type="+type+"&"+"data="+data, (msg)=>{
                    if(typeof(success_callback) == "function"){
                        success_callback(msg);
                    }
                },(msg)=>{

                });
            }
        },
        watch:{
            range_RAM(new_val){
                this.number_RAM = Math.floor(Math.pow(2, new_val-1));
            },
            range_players(new_val){
                this.number_players = 10 * new_val;
            }
        },
        mounted(){
            this.aj_get_lists();
        }
    }
</script>

<style scoped>
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
    width: 35%;
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

button.finish_btn{
    outline: none;
    border: none;
    width: 100%;
    background-color: #0073b7;
    color: white;
    height: 100%;
    line-height: 2.7em;
    font-size: 1.5rem;
}

span.input-element div.mask{
    position: absolute;
    width: 58%;
    height: 35px;
    background-color: rgba(255,255,255, 0.75);
    text-align: center;
}

span.input-element div.mask span.mask-text{
    font-size: 14px;
    line-height: 30px;
    display: inline-block;
    color: rgba(100,100,100,0.75);
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -khtml-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}

button.finish_btn[disabled]{
    background-color:#90a7b5;
}
a{
    cursor: pointer;
}
@media(max-width: 766px){
    div.main-frame{
        padding-top: 2rem;
    }
}

</style>
