<template lang="html">
    <div>
        <section class="mobile-header-bar">
            <span class="left-arrow"><!--<i class="ion-ios-arrow-left"></i>--></span>
            <span class="select_menu" id="select_menu" @click="menu_toggle">
                <span class="text">{{ current_instance_name }}</span><i class="ion-arrow-down-b dropdown-mark " v-bind:class="{transform: markRotate}"></i>
                <div class="dropdown " v-bind:class="{expand: dropdownExpand}">
                    <div class="padding"></div>
                    <div v-for="inst_item in user_list">
                        <a @click="click_menu(inst_item.inst_id)" v-bind:href="'#'+inst_item.inst_id">{{ inst_item.inst_name }}</a>
                    </div>
                    <router-link to="/server_inst/new_inst"><i class="ion-plus"></i> <span class="new_inst_txt">新的世界</span></router-link>
                    <div class="padding"></div>
                </div>
            </span>
            <span class="right-arrow"><!--<i class="ion-ios-arrow-right"></i>--></span>
        </section>

        <div class="inst-sel">
            <div style="margin-bottom:1rem;"><b>实例列表</b></div>
            <div v-for="inst_item in user_list">
                <span class="star">
                    <i class="ion-android-star" v-if="inst_item.star == true"></i>
                    <i class="ion-android-star-outline" v-else></i>
                </span>
                <a :href="'#'+inst_item.inst_id" :class="{selected: inst_item.is_selected}" @click="click_menu(inst_item.inst_id)">{{ inst_item.inst_name }}</a>
            </div>
            <!--new instance-->
            <div>
                <span class="star"> </span>
                <router-link to="/server_inst/new_inst"><i class="ion-plus"></i>&nbsp;&nbsp;&nbsp;<span class="new_inst_txt">新的世界</span></router-link>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        name: "inst-select",
        props: ['inst_id'],
        data(){
            return {
                user_list:[],
                current_instance_id : null,
                current_instance_name: null,
                dropdownExpand:false,
                markRotate: true,
            }
        },
        methods:{
            click_menu(inst_id){
                for(let i in this.user_list){
                    if(this.user_list[i]["inst_id"] == inst_id){
                        this.current_instance_name = this.user_list[i]["inst_name"];
                        this.user_list[i]["is_selected"] = true;
                    }else{
                        this.user_list[i]["is_selected"] = false;
                    }
                }
                this.$emit('click', inst_id);
            },
            menu_toggle(){
                this.markRotate = !this.markRotate;
                this.dropdownExpand = !this.dropdownExpand;
            },
            init_inst_list(msg){
                this.user_list = msg.list;
                this.current_instance_id = msg.current_id;

                for(let i in msg.list){
                    if(this.inst_id != null){
                        if(msg.list[i]['inst_id'] === this.inst_id){
                            this.current_instance_name = msg.list[i]["inst_name"];
                            this.user_list[i]["is_selected"] = true;
                            break;
                        }
                    }else if(msg.list[i]["inst_id"] == msg.current_id){
                        this.current_instance_name = msg.list[i]["inst_name"];
                        this.user_list[i]["is_selected"] = true;
                        break;
                    }
                }
            },
        }
    }
</script>

<style scoped>
/*on desktop*/
section.mobile-header-bar{
        display: none;
    }
    /*including max-width: 767px :-)*/
    @media (max-width: 1200px){
        section.content div.inst-sel-bar{
            display: none;
        }

        section.mobile-header-bar{
            height: 40px;
            background-color: ghostwhite;
            border-bottom: 1px solid lightgrey;
            display: block;
            text-align: center;
        }

        section.mobile-header-bar span.left-arrow,
        section.mobile-header-bar span.select_menu,
        section.mobile-header-bar span.right-arrow
        {
            line-height: 40px;
            font-size: 20px;
            display: inline-block;
            position:relative;
        }

        section.mobile-header-bar span.left-arrow{
            padding-left:10px;
            float:left;
        }

        section.mobile-header-bar span.right-arrow{
            margin-right:0;
            padding-right: 10px;
            float:right;
        }

        section.mobile-header-bar span.select_menu {
            height: 36px;
            margin-top:-2px;
            font-size:14px;
            text-decoration: none;
            box-sizing: border-box;
            border-bottom: 2px solid darkgreen;
            cursor: pointer;
        }

        span.select_menu span.text{
            line-height: 40px;
            display:inline-block;
            margin-right:10px;
        }

        span.select_menu div.dropdown{
            overflow-y:hidden;
            /*height:100px;*/
            height:0;
            background-color: white;
            margin-top:1px;
            box-sizing: border-box;
            border-top:1px solid lightgray;
            box-shadow: 1px 1px 3px #ccc;
            z-index: 10;
        }

        span.select_menu div.dropdown.expand{
            height: auto;
        }

        div.dropdown div.padding{
            height: 10px;
        }

        i.dropdown-mark{
            position: absolute;
            right: 0;
            -webkit-transition: all 300ms;
            -moz-transition: all 300ms;
            -ms-transition: all 300ms;
            -o-transition: all 300ms;
            transition: all 300ms;
        }

        i.dropdown-mark.transform{
            -webkit-transform: rotate(180deg);
            -moz-transform: rotate(180deg);
            -ms-transform: rotate(180deg);
            -o-transform: rotate(180deg);
            transform: rotate(180deg);
        }
        div.dropdown a{
            display: block;
            height: 35px;
            padding-left: 2em;
            padding-right: 2em;
            color: black;
            line-height: 35px;
            width: 100%;
            text-align: center;
        }

        div.dropdown a:hover{
            background-color: #e2e2e2;
        }

        /* hide */
        div.inst-sel{
            display: none;
        }
    }

@media (min-width: 1201px){
    section.content{
        position: relative;
        margin-top: 18px;
    }

    div.inst-sel-bar{
        width:220px;
        height:0;
        float:left;
        display: block;
        padding-left:20px;
        position: relative;
        z-index: 20;
    }

    div.inst-content{
        float:left;
        padding-left:240px;
        width:100%;
        z-index: 10;
    }

    div.inst-sel-bar div.inst-sel{
        width:100%;
        border-right:1px solid #ccc;
        padding-bottom: 10px;
        z-index: 20;
    }

    div.inst-sel a{
        display: inline-block;
        width:170px;
        line-height: 30px;
        height:30px;
        color: black;
        font-size:1.5rem;
        padding-left:0.8rem;
        margin: 0;
        margin-left: 0.2rem;
    }

    div.inst-sel span.star{
        display: inline-block;
        width:18px;
        text-align: center;
        font-size: 21px;
        vertical-align: bottom;
        line-height: 30px;
    }

    div.inst-sel a.selected{
        color:white;
        background-color: mediumpurple;
    }

    div.inst-sel a:hover{
        text-decoration: underline;
    }
}

span.new_inst_txt{
    color: #555;
}
</style>
