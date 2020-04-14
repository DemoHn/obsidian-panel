package config

var defaults = map[string]Value{
	"version":      newString("0.7"),
	"rpc.host":     newString("127.0.0.1"),
	"rpc.port":     newInt(12138),
	"rpc.tls.host": newString("127.0.0.1"),
	"rpc.tls.port": newInt(12338),
}
