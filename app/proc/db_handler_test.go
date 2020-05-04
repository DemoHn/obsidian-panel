package proc

import (
	"reflect"
	"testing"
)

func Test_strinifyEnv(t *testing.T) {
	cases := []struct {
		name   string
		input  map[string]string
		expect string
	}{
		{
			name:   "empty env",
			input:  map[string]string{},
			expect: "",
		},
		{
			name: "normal env",
			input: map[string]string{
				"CWD": "/a/b/c",
			},
			expect: "CWD=\"/a/b/c\"",
		},
		{
			name: "enquote",
			input: map[string]string{
				"CMD": "a\\b\"c",
			},
			expect: "CMD=\"a\\\\b\\\"c\"", // CMD="a\\b\"c"
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			data := stringifyEnv(tt.input)
			if data != tt.expect {
				t.Errorf("unmatched data, expect -> %s, actual -> %s", tt.expect, data)
			}
		})
	}
}

func Test_parseEnv(t *testing.T) {
	cases := []struct {
		name   string
		input  string
		expect map[string]string
	}{
		{
			name:   "empty parse",
			input:  "",
			expect: map[string]string{},
		},
		{
			name:  "normal parse",
			input: `A="12B",B="24C",C123="QQR"`,
			expect: map[string]string{
				"A":    "12B",
				"B":    "24C",
				"C123": "QQR",
			},
		},
		{
			name:  "with quote",
			input: `A="这是一个\"\\",B="normal string "`,
			expect: map[string]string{
				"A": `这是一个"\`,
				"B": "normal string ",
			},
		},
	}

	for _, tt := range cases {
		t.Run(tt.name, func(t *testing.T) {
			out, err := parseEnv(tt.input)
			if err != nil {
				t.Errorf("an error happened: %s", err.Error())
			}

			if !reflect.DeepEqual(out, tt.expect) {
				t.Errorf("not match: expect -> %v, got -> %v", tt.expect, out)
			}
		})
	}
}
