#!/bin/sh
DIR=$(dirname $([ -L $0 ] && readlink -f $0 || echo $0))

DEST_FILE="$(dirname $DIR)/.obsidian_panel.ini"

parse_yaml() {
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

# clear file
echo -e '' > $DEST_FILE

debug="false"
# read config.yaml
eval $(parse_yaml $(dirname $DIR)/config.yaml "config_")

write_circus(){
    cat >> $DEST_FILE <<- EOF
[circus]
endpoint = tcp://127.0.0.1:$config_circus_end_port

EOF

}

write_app(){
    cat >> $DEST_FILE <<- EOF
[watcher:app]

copy_env = True
virtualenv = ./env
working_dir = ./
stdout_stream.class = FileStream
stdout_stream.filename = $config_global_log_file
use_sockets = True
cmd = python launch.py -b app --fd=\$(circus.sockets.app) --debug=$debug --use_reloader=$config_server_use_reloader
numprocesses = $config_server_process_num

[socket:app]
host = 0.0.0.0
port = $config_server_listen_port

EOF
}

write_ftp_manager(){
    cat >> $DEST_FILE <<- EOF
[watcher:ftp_manager]
copy_env = True
virtualenv = ./env
working_dir = ./
cmd = python launch.py -b ftp_manager -p $config_ftp_listen_port --debug=$debug
numprocesses = 1
stdout_stream.class = FileStream
stdout_stream.filename = $config_global_log_file

EOF
}

write_process_watcher(){
    cat >> $DEST_FILE <<- EOF
[watcher:process_watcher]
copy_env = True
virtualenv = ./env
working_dir = ./
cmd = python launch.py -b process_watcher --debug=$debug
numprocesses = 1
stdout_stream.class = FileStream
stdout_stream.filename = $config_global_log_file

EOF
}

write_websocket_server(){
    cat >> $DEST_FILE <<- EOF
[watcher:websocket_server]
copy_env = True
virtualenv = ./env
working_dir = ./
cmd = python launch.py -b websocket_server -p $config_websocket_listen_port --debug=$debug
numprocesses = 1
stdout_stream.class = FileStream
stdout_stream.filename = $config_global_log_file

EOF
}

write_circus
write_app
write_ftp_manager
write_process_watcher
write_websocket_server
