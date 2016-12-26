<template>
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
                                <tr v-for="version in versions">
                                    <td>{{ $index + 1 }}</td>
                                    <td>{{ version.major +"u" + version.minor}}</td>
                                    <td>
                                        <button class="btn btn-primary btn-sm"
                                                type="button"
                                                v-if="version.btn_status.status == 1"
                                                @click="dw_click($index, $event)">&nbsp;&nbsp;下载&nbsp;&nbsp;</button>

                                        <button class="btn btn-primary btn-sm"
                                                type="button"
                                                v-else-if="version.btn_status.status == 2"
                                                disabled
                                                @click="dw_click($index, $event)">&nbsp;{{version.btn_status.progress.toFixed(1)+"%"}}&nbsp;</button>

                                        <button class="btn btn-primary btn-sm"
                                                type="button"
                                                v-else-if="version.btn_status.status == 3"
                                                disabled
                                                @click="dw_click($index, $event)">解压中</button>

                                        <button class="btn btn-primary btn-sm"
                                                type="button"
                                                v-else-if="version.btn_status.status == 4"
                                                disabled
                                                @click="dw_click($index, $event)">已下载</button>

                                        <button class="btn btn-danger btn-sm"
                                                type="button"
                                                v-else-if="version.btn_status.status == 5"
                                                @click="dw_click($index, $event)">下载失败</button>

                                        <button class="btn btn-danger btn-sm"
                                                type="button"
                                                v-else-if="version.btn_status.status == 6"
                                                @click="dw_click($index, $event)">解压失败</button>
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
            let btn_status = this.versions[index].btn_status;
            switch(btn_status.status){
            case FAIL:
            case EXTRACT_FAIL:
                // clear and restart
                btn_status.status = DOWNLOADING;
                var _major = this.versions[index].major;
                var _minor = this.versions[index].minor;
                self._start_downloading(_major, _minor, index);
                break;
            case WAIT:
                btn_status.status = DOWNLOADING;
                var _major = this.versions[index].major;
                var _minor = this.versions[index].minor;
                self._start_downloading(_major, _minor, index);
                break;
            default:
                break;
            }
        }
    }
}
</script>

<style>
</style>
