package apm

import (
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/spf13/cobra"
)

// ApmCmd - 2rd command "apm"
var ApmCmd = &cobra.Command{
	Use:   "apm",
	Short: "main process manager driver",
}

var log = infra.GetCLILogger()

func init() {
	ApmCmd.AddCommand(apmDaemonCmd)
	ApmCmd.AddCommand(apmKillCmd)
}
