package apm

import (
	"github.com/DemoHn/obsidian-panel/app"
	"github.com/DemoHn/obsidian-panel/app/providers"
	"github.com/spf13/cobra"
)

var fg bool
var apmDaemonCmd = &cobra.Command{
	Use:   "daemon",
	Short: "start obsidian-panel daemon",
	Run: func(cmd *cobra.Command, args []string) {
		var err error
		var p *providers.Providers
		if p, err = app.LoadProvidersFromCmd(cmd); err != nil {
			log.PrintError(err)
			return
		}

		if err = p.ProcessManager.StartDaemon(fg); err != nil {
			log.PrintError(err)
			return
		}

		log.PrintOK("Start daemon succeed")
	},
}

func init() {
	apmDaemonCmd.Flags().BoolVarP(&fg, "foreground", "f", false, "start apm on foreground")
}
