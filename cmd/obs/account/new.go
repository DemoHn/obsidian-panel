package account

import (
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/spf13/cobra"
	survey "gopkg.in/AlecAivazis/survey.v1"
)

var log = infra.GetCLILogger()

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
		/**
		var p *providers.Providers
		var err error
		if p, err = app.LoadProvidersFromCmd(cmd); err != nil {
			log.PrintError(err)
			return
		}

		answers := struct {
			Name          string
			Password      string
			PasswordAgain string
			UserType      string `survey:"type"`
		}{}

		log.PrintInfo("Please follow the instructions to create a new user")
		// perform the questions
		err = survey.Ask(qs, &answers)
		if err != nil {
			log.PrintError(err)
			return
		}

		// validators
		if answers.Password != answers.PasswordAgain {
			log.PrintFail("Two passwords not match!")
			return
		}

		// create account
		if err = p.Account.RegisterAdmin(answers.Name, answers.Password); err != nil {
			log.PrintError(err)
			return
		}

		log.PrintOK("user: %s created successfully", answers.Name)
		*/
	},
}
