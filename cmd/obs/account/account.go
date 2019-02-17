package account

import "github.com/spf13/cobra"

// AccountCmd - 2rd command "account"
var AccountCmd = &cobra.Command{
	Use:   "account",
	Short: "manage (admin, normal) accounts of the panel",
}

func init() {
	AccountCmd.AddCommand(newAccountCmd)
}
