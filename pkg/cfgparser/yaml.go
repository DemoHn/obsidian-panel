package cfgparser

import (
	"fmt"

	yaml "gopkg.in/yaml.v2"
)

type yamlMap = map[interface{}]interface{}
type yamlArray = []interface{}

func parseYamlConfig(data []byte) (map[string]interface{}, error) {
	m := make(yamlMap)

	err := yaml.Unmarshal([]byte(data), &m)
	if err != nil {
		return nil, err
	}

	configItems := make(map[string]interface{})
	flattenYamlMap("", m, &configItems)

	return configItems, nil
}

func flattenYamlMap(key string, m yamlMap, items *map[string]interface{}) {
	var kk string
	for k, v := range m {
		// parse key
		validKey := true
		switch k.(type) {
		case string:
			// first level
			if key == "" {
				kk = k.(string)
			} else {
				kk = key + "." + k.(string)
			}
		case int:
			// first level
			if key == "" {
				kk = fmt.Sprintf("%v", k)
			} else {
				kk = fmt.Sprintf("%s.%v", key, k)
			}
		default:
			validKey = false
		}

		// parse value
		if validKey {
			(*items)[kk] = v

			switch v.(type) {
			case yamlMap:
				flattenYamlMap(kk, v.(yamlMap), items)
			case yamlArray:
				tmpMap := make(yamlMap)
				// translate numeric key -> string key
				for index, item := range v.(yamlArray) {
					stringKey := fmt.Sprintf("%v", index)
					tmpMap[stringKey] = item
				}

				flattenYamlMap(kk, tmpMap, items)
			}
		}
	}
}
