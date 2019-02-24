package apm

import (
	"github.com/DemoHn/obsidian-panel/app"
	"github.com/DemoHn/obsidian-panel/util"
	"github.com/spf13/cobra"
)

var force bool
var apmKillCmd = &cobra.Command{
	Use:   "kill",
	Short: "kill obsidian-panel daemon",
	Run: func(cmd *cobra.Command, args []string) {
		var p *app.Providers
		var err error
		// init app
		configPath := cmd.Flag("config").Value.String()
		if p, err = app.GetProviders(configPath, false); err != nil {
			util.LogError(err)
			return
		}

		if err = p.ProcessManager.KillDaemon(force); err != nil {
			util.LogError(err)
		}
	},
}

func init() {
	apmKillCmd.Flags().BoolVarP(&force, "force", "f", false, "kill daemon by force (SIGKILL)")
}
