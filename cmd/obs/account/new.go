package account

import (
	"fmt"

	"github.com/DemoHn/obsidian-panel/app"
	"github.com/spf13/cobra"
	survey "gopkg.in/AlecAivazis/survey.v1"
)

// the questions to ask
var qs = []*survey.Question{
	{
		Name:     "name",
		Prompt:   &survey.Input{Message: "New username:"},
		Validate: survey.Required,
	},
	{
		Name:     "password",
		Prompt:   &survey.Password{Message: "New password (min 6 characters):"},
		Validate: survey.MinLength(6),
	},
	{
		Name:     "passwordAgain",
		Prompt:   &survey.Password{Message: "Repeat your new password:"},
		Validate: survey.MinLength(6),
	},
	{
		Name: "type",
		Prompt: &survey.Select{
			Message: "User type",
			Options: []string{"admin", "user"},
			Default: "admin",
		},
	},
}

var newAccountCmd = &cobra.Command{
	Use: "new",
	Run: func(cmd *cobra.Command, args []string) {
		// init app
		configPath := cmd.Flag("config").Value.String()
		p := app.Init(configPath, false)

		answers := struct {
			Name          string
			Password      string
			PasswordAgain string
			UserType      string `survey:"type"`
		}{}

		// TODO: use a better logger!
		fmt.Println("Please follow the instructions to create a new user")
		// perform the questions
		err := survey.Ask(qs, &answers)
		if err != nil {
			fmt.Println(err.Error())
			return
		}

		// validators
		if answers.Name == "" {
			fmt.Println("Username is empty!")
			return
		}
		if answers.Password != answers.PasswordAgain {
			fmt.Println("Fail: Two passwords not match!")
			return
		}

		// create account
		acct, err := p.Account.RegisterAdmin(answers.Name, answers.Password)
		if err != nil {
			fmt.Println("Fail: ", err.Error())
			return
		}

		fmt.Printf("Create user: %s success", acct.Name)
	},
}
