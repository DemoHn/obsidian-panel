package apm

import (
	"github.com/DemoHn/obsidian-panel/app/providers"
	"github.com/DemoHn/obsidian-panel/util"
	"github.com/spf13/cobra"
)

var force bool
var apmKillCmd = &cobra.Command{
	Use:   "kill",
	Short: "kill obsidian-panel daemon",
	Run: func(cmd *cobra.Command, args []string) {
		var err error
		var p *providers.Providers
		if p, err = util.LoadAppFromCmd(cmd); err != nil {
			log.PrintError(err)
			return
		}

		if err = p.ProcessManager.KillDaemon(force); err != nil {
			log.PrintError(err)
		}
	},
}

func init() {
	apmKillCmd.Flags().BoolVarP(&force, "force", "f", false, "kill daemon by force (SIGKILL)")
}
