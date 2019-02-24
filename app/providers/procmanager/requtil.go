package procmanager

import (
	"net/rpc"
)

func (p *provider) sendRequest(method string, input interface{}, output interface{}) error {
	var err error

	var sockFile string
	if sockFile, err = p.localConfig.FindString("global.sockFile"); err != nil {
		return err
	}

	var client *rpc.Client
	if client, err = rpc.DialHTTP("unix", sockFile); err != nil {
		return err
	}

	return client.Call(method, input, output)
}
