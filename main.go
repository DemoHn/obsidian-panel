package main

import (
	"os"

	"github.com/DemoHn/obsidian-panel/cmd/obs"
)

func main() {
	if err := obs.Execute(); err != nil {
		os.Exit(1)
	}
}
