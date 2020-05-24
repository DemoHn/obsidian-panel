package proc

import (
	"reflect"
	"testing"
)

func TestSplitCommand_OK(t *testing.T) {
	testcases := []string{
		"",
		"asdf",
		"asdf/javac s q r",
		// double quote
		"asdf/javad s q r \"fr om \" d",
		// single quote
		"asdf/javae s q r 'fr om ' d",
		// single quote with multiple spaces
		"'java script'                 -i          good    ",
		// double quote contains single quote
		"node.js \"it's time to change\"",
		// trx spaces
		"Program\\ Files\\\\ husman",
		// trx single quotes
		"\"Program \" \"with\" husman",
		// single quotes
		"/bin/sha -c ''",
		"/bin/shb -c \\'\\'",
		"/bin/shc -c 'Hello \\\" World '",
		"/bin/shd -c ' It'\\'s' time to think'",
		// utf8 + multiple double quotes
		"hk.py -d \"香港记者\" \"跑得快\" 是2真的",
	}

	expectPrograms := []string{
		"",
		"asdf",
		"asdf/javac",
		"asdf/javad",
		"asdf/javae",
		"java script",
		"node.js",
		"Program Files\\",
		"Program ",
		"/bin/sha",
		"/bin/shb",
		"/bin/shc",
		"/bin/shd",
		"hk.py",
	}

	expectArgs := [][]string{
		{},
		{},
		{"s", "q", "r"},
		{"s", "q", "r", "fr om ", "d"},
		{"s", "q", "r", "fr om ", "d"},
		{"-i", "good"},
		{"it's time to change"},
		{"husman"},
		{"with", "husman"},
		{"-c"},
		{"-c", "''"},
		{"-c", "Hello \\\" World "},
		{"-c", " It's time to think"},
		{"-d", "香港记者", "跑得快", "是2真的"},
	}

	for i, s := range testcases {
		program, args, err := SplitCommand(s)
		if err != nil {
			t.Errorf("case %s should NOT have error, but %s occured", s, err)
			return
		}

		if program != expectPrograms[i] {
			t.Errorf("case %s not expect 'program'", s)
			return
		}
		if !reflect.DeepEqual(args, expectArgs[i]) {
			t.Errorf("case %s not expect 'args'", s)
		}
	}
}

func TestSplitCommand_FAIL(t *testing.T) {
	testcases := []string{
		// open single-quote
		"/bin/asha 'ddd",
		"/bin/asha 'It\\'s time to go'",
		// open double-quote
		"/bin/asha 'ddd' \"",
		// end tx
		"/bin/asha \\\\\\",
	}

	for _, s := range testcases {
		_, _, err := SplitCommand(s)
		if err == nil {
			t.Errorf("%s should throw error", s)
		}
	}
}
