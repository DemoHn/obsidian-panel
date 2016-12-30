class BodyParser{
    static serialize(json_body){
        let str = "";
        for(let key in json_body){
            let item = json_body[key];
            let str_item = "";
            if(typeof(item) === "object"){
                str_item = JSON.stringify(item);
            }else{
                str_item = "" + item;
            }
            str_item = encodeURI(str_item);
            key = encodeURI(key);

            str += (key+"="+str_item+"&");
        }
        str = str.slice(0, -1);
        console.log(str);
        return str;
    }
}

export default BodyParser;
