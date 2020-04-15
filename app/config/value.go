package config

import (
	"fmt"
	"strconv"
	"strings"
)

// Value -
type Value struct {
	data     interface{}
	typeHint int
}

// declare type hints
const (
	IntType        = 1
	StringType     = 2
	BoolType       = 3
	IntListType    = 14
	StringListType = 24
)

func (v Value) toString() string {
	switch v.typeHint {
	case IntType, StringType, BoolType:
		return fmt.Sprintf("%v", v.data)
	case IntListType:
		vv, _ := v.data.([]int)
		strs := []string{}
		for _, x := range vv {
			strs = append(strs, strconv.Itoa(x))
		}
		return strings.Join(strs, ",")
	case StringListType:
		vv, _ := v.data.([]string)
		return strings.Join(vv, ",")
	}
	return ""
}

func (v Value) getInt() (int, bool) {
	if v.typeHint == IntType {
		vv, _ := v.data.(int)
		return vv, true
	}
	return 0, false
}

func (v Value) getString() (string, bool) {
	if v.typeHint == StringType {
		vv, _ := v.data.(string)
		return vv, true
	}
	return "", false
}

func (v Value) getBool() (bool, bool) {
	if v.typeHint == BoolType {
		vv, _ := v.data.(bool)
		return vv, true
	}
	return false, false
}

func (v Value) getIntList() ([]int, bool) {
	if v.typeHint == IntListType {
		vv, _ := v.data.([]int)
		return vv, true
	}
	return nil, false
}

func (v Value) getStringList() ([]string, bool) {
	if v.typeHint == StringListType {
		vv, _ := v.data.([]string)
		return vv, true
	}
	return nil, false
}

// internal initialize functions
func newInt(value int) Value {
	return Value{
		data:     value,
		typeHint: IntType,
	}
}

func newString(value string) Value {
	return Value{
		data:     value,
		typeHint: StringType,
	}
}

func newBool(value bool) Value {
	return Value{
		data:     value,
		typeHint: BoolType,
	}
}

func newIntList(value []int) Value {
	return Value{
		data:     value,
		typeHint: IntListType,
	}
}

func newStringList(value []string) Value {
	return Value{
		data:     value,
		typeHint: StringListType,
	}
}

func newFromString(data string, typeHint int) Value {
	switch typeHint {
	case IntType:
		d := 0
		if v, err := strconv.Atoi(data); err == nil {
			d = v
		}
		return Value{
			data:     d,
			typeHint: typeHint,
		}

	case StringType:
		return Value{
			data:     data,
			typeHint: typeHint,
		}
	case BoolType:
		d := false
		if data == "1" {
			d = true
		}
		return Value{
			data:     d,
			typeHint: typeHint,
		}
	case IntListType:
		strs := strings.Split(data, ",")
		final := []int{}
		for _, str := range strs {
			d := 0
			if v, err := strconv.Atoi(str); err == nil {
				d = v
			}
			final = append(final, d)
		}
		return Value{
			data:     final,
			typeHint: typeHint,
		}
	case StringListType:
		strs := strings.Split(data, ",")
		return Value{
			data:     strs,
			typeHint: typeHint,
		}
	}
	return Value{
		data:     data,
		typeHint: StringType,
	}
}
