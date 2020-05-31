package client

import (
	"fmt"
	"net/rpc"

	"github.com/DemoHn/obsidian-panel/util"
)

// SendRequest -
func SendRequest(rootPath string, method string, req interface{}, rsp interface{}) error {
	path, err := util.FindRootPath(rootPath)
	if err != nil {
		return err
	}

	sock := fmt.Sprintf("%s/proc/obs-daemon.sock", path)
	client, err := rpc.DialHTTP("unix", sock)
	if err != nil {
		return err
	}

	return client.Call(method, req, rsp)
}
