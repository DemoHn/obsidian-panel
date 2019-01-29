package cmdspliter

import (
	"testing"

	// goblin
	. "github.com/franela/goblin"
)

func TestSplitCommand(t *testing.T) {
	g := Goblin(t)

	g.Describe("Util > splitCommand()", func() {

		g.It("should pass all tests", func() {
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
				[]string{},
				[]string{},
				[]string{"s", "q", "r"},
				[]string{"s", "q", "r", "fr om ", "d"},
				[]string{"s", "q", "r", "fr om ", "d"},
				[]string{"-i", "good"},
				[]string{"it's time to change"},
				[]string{"husman"},
				[]string{"with", "husman"},
				[]string{"-c"},
				[]string{"-c", "''"},
				[]string{"-c", "Hello \\\" World "},
				[]string{"-c", " It's time to think"},
				[]string{"-d", "香港记者", "跑得快", "是2真的"},
			}

			for i, s := range testcases {
				program, args, err := SplitCommand(s)
				g.Assert(err).Equal(nil)
				g.Assert(program).Equal(expectPrograms[i])
				g.Assert(args).Equal(expectArgs[i])
			}
		})

		g.It("should all throw error", func() {
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
				g.Assert(err == nil).Equal(false)
			}
		})
	})
}
