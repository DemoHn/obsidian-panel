<template lang="html">
    <section class="content">
        <div class="row">
            <div class="col-md-6 col-lg-4">
                <div class="box box-info">
                    <div class="box-header with-border">
                        <h3 class="box-title">Java版本管理</h3>

                        <div class="box-tools pull-right">
                            <button class="btn btn-box-tool" type="button" data-widget="collapse">
                                <i class="fa fa-minus"></i>
                            </button>
                        </div>
                    </div>
                    <div class="box-body">
                        <div class="table-responsive">
                            <table class="table no-margin text-center" id="java_list">
                                <thead>
                                    <tr>
                                        <th>序号</th>
                                        <th>Java版本</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                <tr v-for="(version,index) in versions">
                                    <td>{{ index + 1 }}</td>
                                    <td>{{ version.major +"u" + version.minor}}</td>
                                    <td>
                                        <button class="btn btn-primary btn-sm"
                                                type="button"
                                                v-if="version.btn_status.status == 1"
                                                @click="dw_click(index, event)">&nbsp;&nbsp;下载&nbsp;&nbsp;</button>

                                        <button class="btn btn-primary btn-sm"
                                                type="button"
                                                v-else-if="version.btn_status.status == 2"
                                                disabled
                                                @click="dw_click(index, event)">&nbsp;{{version.btn_status.progress.toFixed(1)+"%"}}&nbsp;</button>

                                        <button class="btn btn-primary btn-sm"
                                                type="button"
                                                v-else-if="version.btn_status.status == 3"
                                                disabled
                                                @click="dw_click(index, event)">解压中</button>

                                        <button class="btn btn-primary btn-sm"
                                                type="button"
                                                v-else-if="version.btn_status.status == 4"
                                                disabled
                                                @click="dw_click(index, event)">已下载</button>

                                        <button class="btn btn-danger btn-sm"
                                                type="button"
                                                v-else-if="version.btn_status.status == 5"
                                                @click="dw_click(index, event)">下载失败</button>

                                        <button class="btn btn-danger btn-sm"
                                                type="button"
                                                v-else-if="version.btn_status.status == 6"
                                                @click="dw_click(index, event)">解压失败</button>
                                    </td>
                                </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<script>
    import WebSocket from "../../lib/websocket.js"
    const WAIT = 1,
DOWNLOADING = 2,
EXTRACTING = 3,
FINISH = 4,
FAIL = 5,
EXTRACT_FAIL = 6;

export default {
    name: 'JavaBinary',
    data : function(){
        return {
            versions : []
        }
    },
    methods: {
        dw_click(index, event) {
            let btn_status = this.versions[index]["btn_status"];
            switch(btn_status.status){
            case FAIL:
            case EXTRACT_FAIL:
                // clear and restart
                btn_status.status = DOWNLOADING;
                var _major = this.versions[index]["major"];
                var _minor = this.versions[index]["minor"];
                this.start_downloading(_major, _minor, index);
                break;
            case WAIT:
                btn_status.status = DOWNLOADING;
                var _major = this.versions[index]["major"];
                var _minor = this.versions[index]["minor"];
                this.start_downloading(_major, _minor, index);
                break;
            default:
                break;
            }
        },

        _find_index_by_hash(_hash){
            var list = this.versions;
            for(var i=0;i<list.length;i++){
                if(list[i]["dw_hash"] == _hash){
                    return i;
                }
            }
            return null;
        },

        init_download_list(result){
            let data = result;

            for(let item in data){
                var _status_model = {
                    "status":data[item]["dw"]["status"],
                    "progress" : data[item]["dw"]["progress"] * 100
                };

                let dw_hash = data[item]["dw"]["current_hash"];
                this.versions.push({
                    "minor" : data[item].minor,
                    "major" : data[item].major,
                    "link"  : data[item].link,
                    "dw_hash" : dw_hash,
                    "btn_status" : _status_model
                });
            }
        },

        start_downloading(major, minor, _index){
            let ws = new WebSocket();
            ws.ajax("GET","/super_admin/api/start_download_java?index="+_index);
        },
        // events
        on_download_start(msg){
            let _hash = msg["hash"];
            let _link = msg["result"];
            // find downloading java version
            for(let i in this.versions){
                if(this.versions[i]["link"] == _link){
                    this.versions[i]["dw_hash"] = _hash;
                    this.versions[i]["btn_status"]["progress"] = 0.0;
                    break;
                }
            }
        },
        on_get_progress(msg){
            let _hash = msg["hash"];
            let _total = msg["result"][1];
            let _dw = msg["result"][0];

            let _index = this._find_index_by_hash(_hash);
            if (_total !== null && _dw !== null && _total > 0) {
                if(this.versions[_index]["btn_status"] != null)
                    this.versions[_index]["btn_status"]["progress"] = _dw / _total * 100;
            }
        },

        on_download_finish(msg){
            let _hash = msg["hash"];
            let _result = msg["result"];

            let _index = this._find_index_by_hash(_hash);
            if(_result){
                this.versions[_index]["btn_status"]["status"] = EXTRACTING;
            }else{
                this.versions[_index]["btn_status"]["status"] = FAIL;
            }
        },

        on_extract_finish(msg){
            let _hash = msg["hash"];
            let _result = msg["result"];
            let _index = this._find_index_by_hash(_hash);
            if(_result){
                this.versions[_index]["btn_status"]["status"] = FINISH; //extract success
            }else{
                this.versions[_index]["btn_status"]["status"] = EXTRACT_FAIL;
            }
        }
    },

    mounted(){
        let ws = new WebSocket();

        ws.ajax("GET","/super_admin/api/get_java_download_list", (msg)=>{
            this.init_download_list(msg);
        })
        ws.bind("_download_start", this.on_download_start);
        ws.bind("_extract_finish", this.on_extract_finish);
        ws.bind("_get_progress", this.on_get_progress);
        ws.bind("_download_finish", this.on_download_finish);
    }
}
    </script>

<style>

</style>
