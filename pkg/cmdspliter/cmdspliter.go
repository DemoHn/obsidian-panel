// Package cmdspliter intends to immitate bash way to split a string command to
// an array of arguments
//
// For example:
// "/bin/cmd -f 'a.zip b.zip' -g" => ["/bin/cmd", "-f", "'a.zip b.zip'", "-g"]
package cmdspliter

import "fmt"

const (
	TK_NUL  uint8 = 0 // null char (ignored)
	TK_TX   uint8 = 1 // transcode char
	TK_CHAR uint8 = 2 // normal char
	TK_SPX  uint8 = 3 // space (separator)
	TK_SQ   uint8 = 4 // single quote
	TK_DQ   uint8 = 5 // double quote
)

// SplitCommand - separate a string command to progarm and args
func SplitCommand(command string) (program string, args []string, err error) {
	// single-quote start/stop index array
	sqarr := []int{}
	// double-quote start/stop index array
	dqarr := []int{}

	// round 1: handle trx chars
	tks := make([]uint8, 0)
	cursor := TK_CHAR
	for _, r := range command {
		switch r {
		case '\\':
			cursor = TK_TX
		case '\'':
			cursor = TK_SQ
		case '"':
			cursor = TK_DQ
		case ' ':
			cursor = TK_SPX
		default:
			cursor = TK_CHAR
		}

		tks = append(tks, cursor)
	}

	// round 2: handle single-quoted strs
	squote := false
	for i, tk := range tks {
		if squote == false {
			if tk == TK_SQ && (i > 0 && tks[i-1] != TK_TX || i == 0) {
				squote = true
				sqarr = []int{i}
			}
		} else {
			// util another single-quote occurs...
			if tk == TK_SQ {
				squote = false
				sqarr = append(sqarr, i)

				// transcode chars from start -> stop
				for j := sqarr[0] + 1; j < sqarr[1]; j++ {
					tks[j] = TK_CHAR
				}
			}
		}
	}
	// round 3: transcode tokens
	for i, tk := range tks {
		if tk == TK_TX {
			if i < len(tks)-1 {
				tks[i] = TK_NUL
				tks[i+1] = TK_CHAR
				// last char (error handling)
			}
		}
	}

	// round 4: double-quote
	dquote := false
	for i, tk := range tks {
		if dquote == false {
			if tk == TK_DQ {
				dquote = true
				dqarr = []int{i}
			}
		} else {
			if tk == TK_DQ {
				dquote = false
				dqarr = append(dqarr, i)

				// transcode chars from start -> stop
				for j := dqarr[0] + 1; j < dqarr[1]; j++ {
					tks[j] = TK_CHAR
				}
			}
		}
	}

	// round 5: handle tokens
	finalArgs := make([]string, 0)
	quoteFlag := TK_NUL
	enterFlag := false

	argStr := make([]rune, 0)
	for i, tk := range tks {
		// change flag status
		switch tk {
		case TK_DQ, TK_SQ:
			if quoteFlag == tk {
				quoteFlag = TK_NUL
			} else if quoteFlag == TK_NUL {
				quoteFlag = tk
			} else {
				argStr = append(argStr, []rune(command)[i])
			}
		case TK_SPX:
			if quoteFlag == TK_NUL {
				enterFlag = true
			} else {
				argStr = append(argStr, []rune(command)[i])
			}
		case TK_CHAR:
			argStr = append(argStr, []rune(command)[i])
		}

		// append string to args
		if enterFlag == true {
			enterFlag = false
			// clear argStr
			if len(argStr) > 0 {
				finalArgs = append(finalArgs, string(argStr))
			}
			argStr = argStr[:0]
		}
	}

	// throw error first
	if quoteFlag != TK_NUL {
		msg := "non-closed single-quote"
		if quoteFlag == TK_DQ {
			msg = "non-closed double-quote"
		}

		err = fmt.Errorf("Parse Error: %s", msg)
		return
	}
	if len(tks) > 0 && tks[len(tks)-1] == TK_TX {
		err = fmt.Errorf("Invalid escape at the end char")
		return
	}

	// insert final argument
	if len(argStr) > 0 {
		finalArgs = append(finalArgs, string(argStr))
	}

	// export data
	if len(finalArgs) > 0 {
		program = finalArgs[0]
	} else {
		program = ""
	}

	if len(finalArgs) > 1 {
		args = finalArgs[1:]
	} else {
		args = []string{}
	}

	return
}
