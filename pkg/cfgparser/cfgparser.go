// Package cfgparser is intended to manage config from a file (usually a YAML configlet).
// It's still in internal testing stage, which means not public accessible.
package cfgparser

import (
	"fmt"
	"io/ioutil"
	"os"
	"regexp"
)

// MacroParserFunc - macro parser function
type MacroParserFunc func(key string, item interface{}) interface{}

// Config type
type Config struct {
	configType  string
	configItem  map[string]interface{}
	macroParser MacroParserFunc
}

// default macro parser - parse ${ENV_VAR} to environment variables
var envMacroParser = func(key string, item interface{}) interface{} {
	// replace $HOME -> <homeDir>
	re := regexp.MustCompile("\\$\\{([^{}]+)\\}")
	// if item is string to replace
	if itemStr, ok := item.(string); ok {
		return re.ReplaceAllStringFunc(itemStr, func(src string) string {
			rawKey := re.FindStringSubmatch(src)[1]
			return os.Getenv(rawKey)
		})
	}

	return item
}

// New - initialize a new config instance
func New(configType string) *Config {
	return &Config{
		configType:  configType,
		configItem:  map[string]interface{}{},
		macroParser: envMacroParser,
	}
}

// SetMacroParser - set macro parser to replace macros like "${HOME}", "${TMP}", etc.
func (config *Config) SetMacroParser(parser MacroParserFunc) {
	config.macroParser = parser
}

// Load - parse & load from a file
// currently only supports "yaml"
func (config *Config) Load(file string) error {
	fd, err := os.Open(file)
	if err != nil {
		return err
	}
	defer fd.Close()

	// read all
	data, errRead := ioutil.ReadAll(fd)
	if errRead != nil {
		return errRead
	}
	// then parse config
	errParse := config.parseConfig(data)
	if errParse != nil {
		return errParse
	}
	// finish
	return nil
}

// LoadFromData - instead of loading config from a file,
// you can directly inject data
func (config *Config) LoadFromData(data []byte) error {
	errParse := config.parseConfig(data)

	if errParse != nil {
		return errParse
	}

	return nil
}

// LoadDefault - load config from default value
func (config *Config) LoadDefault(defaultConf map[string]interface{}) {
	for k, v := range defaultConf {
		config.configItem[k] = v
	}

	config.executeMacro()
	config.resolveDepConfig()
}

// Find - find config value from key.
func (config *Config) Find(key string) (result interface{}, err error) {
	if value, ok := config.configItem[key]; ok {
		result = value
		err = nil
		return
	}

	err = fmt.Errorf("Config key `%s` not found", key)
	return
}

// FindString - find config value and convert it to string
func (config *Config) FindString(key string) (string, error) {
	val, err := config.Find(key)
	if err != nil {
		return "", err
	}

	if valStr, ok := val.(string); ok {
		return valStr, nil
	}

	return "", fmt.Errorf("Config key `%s` is not a string value", key)
}

// FindInt - find config value and convert it to string
func (config *Config) FindInt(key string) (int, error) {
	val, err := config.Find(key)
	if err != nil {
		return 0, err
	}

	if valInt, ok := val.(int); ok {
		return valInt, nil
	}

	return 0, fmt.Errorf("Config key `%s` is not a int value", key)
}

// FindBool - find config value and convert it to bool
func (config *Config) FindBool(key string) (bool, error) {
	val, err := config.Find(key)
	if err != nil {
		return false, err
	}

	if valBool, ok := val.(bool); ok {
		return valBool, nil
	}

	return false, fmt.Errorf("Config key `%s` is not a bool value", key)
}

// resolveDepConfig -
// to support configValue like `$(<var name>)`
// e.g.:
// global.dir = /var/www
// global.sockFile = $(global.dir)/apm.sock -> global.sockFile = /var/www/apm.sock
func (config *Config) resolveDepConfig() {

	for k, v := range config.configItem {
		// only work for string item
		if strValue, ok := v.(string); ok {
			config.configItem[k] = config.mutateConfigValue(strValue)
		}
	}
}

func (config *Config) mutateConfigValue(oldValue string) string {
	re := regexp.MustCompile("\\$\\(([a-zA-Z0-9\\.]+)\\)")

	return re.ReplaceAllStringFunc(oldValue, func(key string) string {
		// get rawKey first
		// rawKey = $1, e.g.: key = $(config.dir), rawKey = config.dir
		rawKey := re.FindStringSubmatch(key)[1]
		// if corresponding key has found and it's a string
		// return the replaced value, otherwise return the original.
		if newValue, err := config.Find(rawKey); err == nil {
			if newValueStr, ok := newValue.(string); ok {
				return newValueStr
			}
			return oldValue
		}

		return oldValue
	})
}

func (config *Config) executeMacro() {
	for k, v := range config.configItem {
		config.configItem[k] = config.macroParser(k, v)
	}
}

// parseConfig - parse config from data
func (config *Config) parseConfig(data []byte) (err error) {
	switch config.configType {
	case "yaml":
		{
			config.configItem, err = parseYamlConfig(data)
			if err != nil {
				return err
			}

			config.executeMacro()
			config.resolveDepConfig()
			return nil
		}
	}

	return fmt.Errorf("Config Type `%s` not found", config.configType)
}
