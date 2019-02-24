package account

import (
	"github.com/DemoHn/obsidian-panel/app"
	"github.com/DemoHn/obsidian-panel/util"
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
			Options: []string{"admin"},
			Default: "admin",
		},
	},
}

var newAccountCmd = &cobra.Command{
	Use:   "new",
	Short: "create new account by CLI",
	Run: func(cmd *cobra.Command, args []string) {
		var p *app.Providers
		var err error
		// init app
		configPath := cmd.Flag("config").Value.String()
		if p, err = app.GetProviders(configPath, false); err != nil {
			util.LogError(err)
			return
		}

		answers := struct {
			Name          string
			Password      string
			PasswordAgain string
			UserType      string `survey:"type"`
		}{}

		util.LogInfo("Please follow the instructions to create a new user")
		// perform the questions
		err = survey.Ask(qs, &answers)
		if err != nil {
			util.LogError(err)
			return
		}

		// validators
		if answers.Password != answers.PasswordAgain {
			util.LogFail("Two passwords not match!")
			return
		}

		// create account
		acct, err := p.Account.RegisterAdmin(answers.Name, answers.Password)
		if err != nil {
			util.LogError(err)
			return
		}

		util.LogOK("user: %s created successfully", acct.Name)
	},
}
