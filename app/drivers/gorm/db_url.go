package gorm

import (
	"fmt"
	"strings"

	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/DemoHn/obsidian-panel/infra/config"
)

// GenerateDatabaseURL - generate a url for gorm from plain parameters
// Example: user:password@tcp(127.0.0.1:3306)/mce_main?parseTime=true&charset=utf8
func GenerateDatabaseURL(inf *infra.Infrastructure) (string, error) {
	var err error
	var dbType string

	config := inf.GetConfig()
	if dbType, err = config.FindString("database.type"); err != nil {
		return "", err
	}
	if dbType == "mysql" {
		return genMysql(config)
	}
	if dbType == "sqlite" {
		return genSqlite(config)
	}

	return "", fmt.Errorf("unsupported db type:%s", dbType)
}

// internal functions
func genMysql(config *config.Config) (string, error) {
	var err error
	// required fields
	var user, password, host, name string
	var port int
	var fields = map[string]*string{
		"database.user":     &user,
		"database.password": &password,
		"database.host":     &host,
		"database.name":     &name,
	}

	for k, v := range fields {
		var strv string
		if strv, err = config.FindString(k); err != nil {
			return "", err
		}

		*v = strv
	}
	// get port
	if port, err = config.FindInt("database.port"); err != nil {
		return "", err
	}

	// get options
	var hasOptions = false
	var options interface{}
	var optionsArr []string
	if options, err = config.Find("database.options"); err == nil {
		// options should be a map
		if optionsMap, ok := options.(map[interface{}]interface{}); ok {
			hasOptions = true
			for k, v := range optionsMap {
				optionsArr = append(optionsArr, fmt.Sprintf("%v=%v", k, v))
			}
		}
	}

	// join url
	dbURL := fmt.Sprintf("%s:%s@tcp(%s:%d)/%s", user, password, host, port, name)
	if hasOptions {
		dbURL = fmt.Sprintf("%s?%s", dbURL, strings.Join(optionsArr, "&"))
	}
	return dbURL, nil
}

func genSqlite(config *config.Config) (string, error) {
	var path string
	var err error
	if path, err = config.FindString("database.path"); err != nil {
		return "", err
	}

	return path, nil
}
