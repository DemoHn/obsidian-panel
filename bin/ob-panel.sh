#!/bin/sh

DIR=$(dirname $([ -L $0 ] && readlink -f $0 || echo $0))

_parse_yaml() {
   local prefix=$2
   local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
   sed -ne "s|^\($s\)\($w\)$s:$s\"\(.*\)\"$s\$|\1$fs\2$fs\3|p" \
        -e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
   awk -F$fs '{
      indent = length($1)/2;
      vname[indent] = $2;
      for (i in vname) {if (i > indent) {delete vname[i]}}
      if (length($3) > 0) {
         vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
         printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
      }
   }'
}

cmd_circusctl(){
    eval $(_parse_yaml $(dirname "$DIR")/config.yaml "config_")
    circusctl --endpoint=tcp://127.0.0.1:$config_circus_end_port --timeout 3 $@
}

start(){
    echo "Start obsidian-panel..."
    sh $DIR/gen.circus.sh
    redis-server --daemonize yes
    cd $DIR/../
    circusd .obsidian_panel.ini --daemon
    cmd_circusctl start
}

status(){
    cmd_circusctl status
}

stop(){
    echo "Stop obsidian-panel..."
    cmd_circusctl stop
}

clear(){
    echo "Unimplemented."
}

restart(){
    echo "Restart obsidian-panel..."
    # generate ini file
    sh $DIR/gen.circus.sh
    redis-server --daemonize yes
    cd $DIR/../
    circusd .obsidian_panel.ini --daemon

    cmd_circusctl restart
}

case "$1" in
  start)
      start
      ;;
  stop)
      stop
      ;;
  clear)
      clear
      ;;
  restart)
      restart
      ;;
  status)
      status
      ;;
  *)
    echo "Usage: $0 {start|stop|restart|status|clear}"
esac
