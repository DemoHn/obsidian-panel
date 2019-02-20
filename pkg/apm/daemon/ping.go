package daemon

import (
	"fmt"
	"net/rpc"
	"os"
	"time"

	"github.com/DemoHn/obsidian-panel/pkg/apm/infra/config"
	"github.com/DemoHn/obsidian-panel/pkg/apm/infra/logger"

	"github.com/DemoHn/obsidian-panel/pkg/apm/master"
)

// Ping - to test if daemon has been started and available to receive data
func Ping() error {
	return ping()
}

// PingTimeout - ping util timeout
func PingTimeout(interval time.Duration, timeout time.Duration) error {
	var err error
	var elTime = time.Duration(0)

	log := logger.Get()
	// loop
	for {
		if err = ping(); err == nil {
			return nil
		}
		// show error
		log.Debugf("[apm] ping error: %s", err.Error())

		<-time.After(interval)
		elTime += interval

		if elTime > timeout {
			return fmt.Errorf("ping timeout")
		}
	}
}

// internal funtion
func ping() error {
	var err error
	configN := config.Get()

	// find sockFile
	var sockFile string
	if sockFile, err = configN.FindString("global.sockFile"); err != nil {
		return err
	}
	// ensure file exists
	if _, err = os.Stat(sockFile); os.IsNotExist(err) {
		return err
	}

	// ping data
	var client *rpc.Client
	if client, err = rpc.DialHTTP("unix", sockFile); err != nil {
		return err
	}

	// send request
	var req = master.PingRequest{}
	var resp = master.PingResponse{}
	if err = client.Call("Tower.Ping", &req, &resp); err != nil {
		return err
	}

	if resp.Info != "pong" {
		return fmt.Errorf("Invalid response data: %s, expected 'pong'", resp)
	}
	return nil
}
