package apm

import (
	"github.com/DemoHn/obsidian-panel/app"
	"github.com/DemoHn/obsidian-panel/util"
	"github.com/spf13/cobra"
)

var fg bool
var apmDaemonCmd = &cobra.Command{
	Use:   "daemon",
	Short: "start obsidian-panel daemon",
	Run: func(cmd *cobra.Command, args []string) {
		// init app
		configPath := cmd.Flag("config").Value.String()
		p := app.Init(configPath, false)

		if err := p.ProcessManager.StartDaemon(fg); err != nil {
			util.LogError(err)
		}
	},
}

func init() {
	apmDaemonCmd.Flags().BoolVarP(&fg, "foreground", "f", false, "start apm on foreground")
}
