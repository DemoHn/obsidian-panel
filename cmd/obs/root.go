package obs

import (
	"github.com/DemoHn/obsidian-panel/app"
	"github.com/DemoHn/obsidian-panel/cmd/obs/account"
	"github.com/DemoHn/obsidian-panel/cmd/obs/apm"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/spf13/cobra"
)

var log = infra.GetCLILogger()

var rootCmd = &cobra.Command{
	Use:     "obs",
	Short:   "obsidian-panel main command",
	Version: "0.7.0",
	Run: func(cmd *cobra.Command, args []string) {
		var err error
		var appInstance *app.App
		if appInstance, err = app.LoadAppFromCmd(cmd); err != nil {
			log.PrintError(err)
			return
		}

		log.PrintError(appInstance.Start())
	},
	SilenceUsage: true,
}

// Execute - execute `obs` command
func Execute() error {
	return rootCmd.Execute()
}

func init() {
	// add sub-command
	rootCmd.AddCommand(account.RootCmd)
	rootCmd.AddCommand(apm.RootCmd)

	// add flags
	rootCmd.PersistentFlags().StringP("config", "c", "", "config filepath")
	rootCmd.PersistentFlags().BoolP("debug", "d", true, "debug mode")
}
