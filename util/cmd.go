package util

import (
	"github.com/DemoHn/obsidian-panel/app"
	"github.com/DemoHn/obsidian-panel/app/providers"
	"github.com/spf13/cobra"
)

// LoadAppFromCmd - init and get app instance from cobra.Command object
// directly. This is usually for further manipulation after app initialized.
func LoadAppFromCmd(cmd *cobra.Command) (*app.App, error) {
	app, err := loadAppFromCmd(cmd)
	if err != nil {
		return nil, err
	}

	return app, nil
}

// LoadProvidersFromCmd - init app and get providers from cobra.Command object
// directly. This is usually for further manipulation after app initialized.
func LoadProvidersFromCmd(cmd *cobra.Command) (*providers.Providers, error) {
	app, err := loadAppFromCmd(cmd)
	if err != nil {
		return nil, err
	}

	return app.GetProviders(), nil
}

func loadAppFromCmd(cmd *cobra.Command) (*app.App, error) {
	var err error
	var configPath = ""
	var debugMode = false

	// init flags
	flagset := cmd.Flags()
	if configPath, err = flagset.GetString("config"); err != nil {
		return nil, err
	}
	if debugMode, err = flagset.GetBool("debug"); err != nil {
		return nil, err
	}

	var appInstance *app.App
	if appInstance, err = app.New(configPath, debugMode); err != nil {
		return nil, err
	}

	return appInstance, nil
}
