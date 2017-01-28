<template lang="html">
    <div class="wrap">
        <div><span class="lb">当前版本：</span> <span class="version">{{ current_version }}</span></div>
        <div v-if="check_status == 0"><span class="lb-gray">正在检查更新 <i class="fa fa-spinner fa-spin fa-fw"></i></span></div>
        <div v-if="check_status == 1">
            <span class="lb-gray">更新检查失败 &nbsp;&nbsp;<button class="btn btn-default btn-xs" @click="check_update">&nbsp;重试&nbsp;</button></span>
        </div>
        <div v-if="check_status == 2">
            <div v-if="is_newest">
                <span class="lb-gray">目前已是最新版本</span>
            </div>
            <div v-if="!is_newest">
                <span class="lb">最新版本：</span> <span class="version">{{ newest_version }}</span>
                <!-- version info-->
                <div class="version-info" v-if="expand_version_info">
                    <div>
                        <span class="lb-gray">发布时间:</span> <div class="lb-blue info_note">{{ newest_release_date }}</div>
                    </div>
                    <div>
                        <span class="lb-gray">更新说明:</span><div class="lb-blue info_note">{{ newest_release_note }}</div>
                    </div>
                </div>
                <div><a class="toggle_a" v-if="!expand_version_info" @click="toggle_exp">展开版本信息</a><a class="toggle_a" v-if="expand_version_info" @click="toggle_exp">收回版本信息</a></div>
                <br>
                <div v-if="update_status == 0">
                    <span class="lb-gray">开始更新前，请务必<b>关闭</b>所有活跃的Minecraft服务器！</span><br>
                    <button class="btn btn-primary btn-sm" @click="execute_update">更新</button>
                </div>
                <div v-if="update_status == 1">
                    <button class="btn btn-primary btn-sm" disabled>更新中 <i class="fa fa-spinner fa-spin fa-fw"></i></button>
                </div>
                <div v-if="update_status == 2">
                    <span class="lb-gray">更新失败</span><br>
                    <button class="btn btn-danger btn-sm" @click="execute_update">重试</button>
                </div>
                <div v-if="update_status == 3">
                    <span class="lb-gray">更新完成，请点击「重新启动」以重启面板！</span><br>
                    <button class="btn btn-danger btn-sm" @click="reboot">重新启动</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    import WebSocket from "../../lib/websocket.js"

    let ws = new WebSocket();
    export default {
        name : 'update-checker',
        data(){
            return {
                "current_version" : "",
                "check_status" : 0,
                "update_status": 0,
                "is_newest" : false,
                "expand_version_info" : false,
                // newest version
                "newest_version":"",
                "newest_release_note":"",
                "newest_release_date":""
            }
        },
        methods:{
            toggle_exp(){
                this.expand_version_info = ! this.expand_version_info;
            },
            get_current_version(){
                let v = this;
                this.aj_get_current_version((msg)=>{
                    v.current_version = msg;
                });
            },
            check_update(){
                let v = this;
                v.check_status = 0;
                this.aj_check_update_info((msg)=>{
                    v.is_newest = msg.is_newest;
                    v.check_status = 2; // success
                    if(!msg.is_newest){
                        v.newest_version = msg.version;
                        v.newest_release_date = msg.publish_date;
                        v.newest_release_note = msg.release_note;
                    }
                },(code)=>{
                    v.check_status = 1; // fail
                });
            },
            execute_update(){
                let v = this;
                v.update_status = 1;
                this.aj_execute_update((msg)=>{
                    if(msg == false){
                        v.update_status = 2;
                    }else{
                        v.update_status = 3;
                    }
                },(code)=>{
                    v.update_status = 2;
                });
            },
            reboot(){
                this.aj_reboot();
            },
            aj_execute_update(callback, cb_error){
                ws.ajax("GET","/super_admin/settings/execute_update",(msg)=>{
                    if(typeof(callback) === "function"){
                        callback(msg);
                    }
                },(code)=>{
                    if(typeof(cb_error) === "function"){
                        cb_error(code);
                    }
                })
            },
            aj_reboot(){
                ws.ajax("GET","/super_admin/settings/reboot",(msg)=>{
                    if(typeof(callback) === "function"){
                        callback(msg);
                    }
                })
            },
            aj_get_current_version(callback){
                ws.ajax("GET","/super_admin/settings/get_current_version",(msg)=>{
                    if(typeof(callback) === "function"){
                        callback(msg);
                    }
                })
            },
            aj_check_update_info(callback, cb_error){
                ws.ajax("GET","/super_admin/settings/check_newest_release",(msg)=>{
                    if(typeof(callback) === "function"){
                        callback(msg);
                    }
                },(code)=>{
                    if(typeof(cb_error) === "function"){
                        cb_error(code);
                    }

                })
            }
        },
        mounted(){
            this.get_current_version();
            this.check_update();
        }
    }
</script>

<style scoped>
div.wrap{
    margin-top: 1rem;
}

span.lb{
    line-height: 2.5rem;
    font-size: 1.5rem;
}

span.lb-gray{
    line-height: 2.5rem;
    color: #888;
    font-size: 1.5rem;
}

div.version-info{
    padding-left: 1rem;
}

div.lb-blue{
    line-height: 2rem;
    color: navy;
    font-size: 1.3rem;
}
div.info_note{
     padding-left: 3rem;
}
a.toggle_a{
    cursor: pointer;
}
</style>
