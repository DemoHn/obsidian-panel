package obs

import (
	"github.com/DemoHn/obsidian-panel/app"
	//"github.com/DemoHn/obsidian-panel/cmd/obs/account"
	"github.com/DemoHn/obsidian-panel/cmd/obs/apm"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/spf13/cobra"
)

var (
	rootDir string
	debug   bool
)
var rootCmd = &cobra.Command{
	Use:     "obs",
	Short:   "obsidian-panel main command",
	Version: "0.7.0",
	Run: func(cmd *cobra.Command, args []string) {
		inst, err := app.New(rootDir, debug)
		if err != nil {
			infra.LogT.PrintError(err)
			return
		}

		infra.LogT.PrintError(app.Start(inst))
	},
	SilenceUsage: true,
}

// Execute - execute `obs` command
func Execute() error {
	return rootCmd.Execute()
}

func init() {
	// add sub-command
	//rootCmd.AddCommand(account.RootCmd)
	rootCmd.AddCommand(apm.RootCmd)

	// add flags
	rootCmd.PersistentFlags().StringVar(&rootDir, "root-dir", "", "panel operation data root path")
	rootCmd.PersistentFlags().BoolVarP(&debug, "debug", "d", true, "debug mode")
}
