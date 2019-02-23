package apm

import "github.com/spf13/cobra"

// ApmCmd - 2rd command "apm"
var ApmCmd = &cobra.Command{
	Use:   "apm",
	Short: "main process manager driver",
}

func init() {
	ApmCmd.AddCommand(apmDaemonCmd)
}
