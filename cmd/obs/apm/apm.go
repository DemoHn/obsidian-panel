package apm

import (
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/spf13/cobra"
)

// RootCmd - 2rd command "apm"
var RootCmd = &cobra.Command{
	Use:   "apm",
	Short: "main process manager driver",
}

var log = infra.GetCLILogger()

func init() {
	RootCmd.AddCommand(apmDaemonCmd)
	RootCmd.AddCommand(apmKillCmd)
}
