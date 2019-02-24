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
		// init app
		configPath := cmd.Flag("config").Value.String()
		p := app.Init(configPath, false)

		if err := p.ProcessManager.KillDaemon(force); err != nil {
			util.LogError(err)
		}
	},
}

func init() {
	apmKillCmd.Flags().BoolVarP(&force, "force", "f", false, "kill daemon by force (SIGKILL)")
}
