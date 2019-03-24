package account

import "github.com/spf13/cobra"

// RootCmd - 2rd command "account"
var RootCmd = &cobra.Command{
	Use:   "account",
	Short: "manage (admin, normal) accounts of the panel",
}

func init() {
	RootCmd.AddCommand(newAccountCmd)
}
