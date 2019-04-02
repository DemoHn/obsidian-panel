package drivers

import (
	"github.com/DemoHn/obsidian-panel/app/drivers/grpc"
	"github.com/DemoHn/obsidian-panel/app/drivers/sqlite"
	"github.com/DemoHn/obsidian-panel/app/drivers/srpc"
	"github.com/DemoHn/obsidian-panel/infra"
)

// Drivers - driver type
type Drivers struct {
	// Sqlite - the raw wrapper of raw Sqlite driver
	Sqlite *sqlite.Driver
	// Grpc - grpc wrapper, with middlewares automatically loaded
	// when init
	Grpc *grpc.Driver
	// Srpc - Golang's internal rpc package wrapper. will be deprecated
	// in the future
	Srpc *srpc.Driver
}

// Init - init drivers after config & other infras loaded
func Init(config *infra.Config) (*Drivers, error) {
	var err error
	// init sqlite
	var sqliteDriver *sqlite.Driver
	if sqliteDriver, err = sqlite.New(config); err != nil {
		return nil, err
	}

	// init grpc
	var grpcDriver *grpc.Driver
	if grpcDriver, err = grpc.New("127.0.0.1", 12318); err != nil {
		return nil, err
	}

	return &Drivers{
		Sqlite: sqliteDriver,
		Grpc:   grpcDriver,
		Srpc:   nil,
	}, nil
}

// Close - close all drivers as teardown
func Close() error {
	return nil
}
