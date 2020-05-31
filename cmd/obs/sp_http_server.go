package obs

import (
	"fmt"
	"os"

	"github.com/DemoHn/obsidian-panel/app"
	"github.com/DemoHn/obsidian-panel/app/api"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/spf13/cobra"
)

var httpServerCmd = &cobra.Command{
	Use:   "api-server",
	Short: "start internal api-server (HTTP) to control the panel",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("===========")
		fmt.Println(os.Environ())
		appI, err := app.New(rootDir, debug)
		if err != nil {
			infra.LogT.PrintError(err)
			return
		}
		if err := api.StartServer(appI); err != nil {
			infra.LogT.PrintError(err)
			return
		}

		infra.LogT.PrintOK("start api server success")
	},
}

func init() {
	sysProcCmd.AddCommand(httpServerCmd)
}
