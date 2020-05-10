package obs

import (
	"time"

	"github.com/DemoHn/obsidian-panel/app"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/spf13/cobra"
)

var (
	rootDir string
	debug   bool
	ctrlOp  string
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

		// read ctrlOp
		switch ctrlOp {
		case "start":
			startApp(inst, false)
		case "stop":
			stopApp(inst)
		case "restart":
			stopApp(inst)
			// sleep 500ms
			time.Sleep(500 * time.Millisecond)
			startApp(inst, false)
		default:
			startApp(inst, true)
		}
	},
	SilenceUsage: true,
}

func startApp(inst *app.App, foreground bool) {
	if err := app.Start(inst, foreground); err != nil {
		infra.LogT.PrintError(err)
	}
}

func stopApp(inst *app.App) {
	if err := app.Stop(inst); err != nil {
		infra.LogT.PrintError(err)
	} else {
		infra.LogT.PrintOK("stop panel success!")
	}
}

// Execute - execute `obs` command
func Execute() error {
	return rootCmd.Execute()
}

func init() {
	// add sub-command
	//rootCmd.AddCommand(account.RootCmd)	

	// add flags
	rootCmd.PersistentFlags().StringVar(&rootDir, "root-dir", "", "panel operation data root path")
	rootCmd.PersistentFlags().BoolVarP(&debug, "debug", "d", false, "debug mode")

	rootCmd.Flags().StringVarP(&ctrlOp, "s", "s", "", "start/stop/restart panel control")
}
