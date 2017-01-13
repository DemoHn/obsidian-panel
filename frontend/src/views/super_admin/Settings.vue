<template lang="html">
    <section class="content">
        <div class="row">
            <div class="col-md-5">
                <div class="box box-info">
                    <div class="box-header with-border">
                        <h3 class="box-title">密码设置</h3>

                        <div class="box-tools pull-right">
                            <button class="btn btn-box-tool" type="button" data-widget="collapse">
                                <i class="fa fa-minus"></i>
                            </button>
                        </div>
                    </div>
                    <div class="box-body" id="password_settings">
                        <div class="form-group">
                            <div class="col-xs-4">
                                <label for="">旧密码</label>
                            </div>

                            <div class="col-xs-6">
                                <input
                                    type="password"
                                    class="form-control"
                                    id="old_password"
                                    name="old_password"
                                    v-model="ori_passwd">
                            </div>
                        </div>
                        <br/><br/>
                        <div class="form-group">
                            <div class="col-xs-4">
                                <label for="">新密码</label>
                            </div>

                            <div class="col-xs-6">
                                <input
                                    type="password"
                                    class="form-control"
                                    id="old_password"
                                    name="old_password"
                                    v-model="new_passwd">
                            </div>
                        </div>
                        <br><br>
                        <div class="form-group">
                            <div class="col-xs-12">
                                <button class="btn btn-primary btn-sm">修改</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<script>
</script>

<style>

</style>
