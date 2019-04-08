package util

import "fmt"

func addErrorTag(tag string, err error) error {
	return fmt.Errorf("%s: %s", tag, err.Error())
}
