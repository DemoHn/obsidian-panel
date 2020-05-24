package proc

// cmdspliter intends to immitate bash way to split a string command to
// an array of arguments
//
// For example:
// "/bin/cmd -f 'a.zip b.zip' -g" => ["/bin/cmd", "-f", "'a.zip b.zip'", "-g"]

import "fmt"

const (
	tkNUL  uint8 = 0 // null char (ignored)
	tkTX   uint8 = 1 // transcode char
	tkCHAR uint8 = 2 // normal char
	tkSPX  uint8 = 3 // space (separator)
	tkSQ   uint8 = 4 // single quote
	tkDQ   uint8 = 5 // double quote
)

// SplitCommand - separate a string command to progarm and args
func SplitCommand(command string) (program string, args []string, err error) {
	// single-quote start/stop index array
	sqarr := []int{}
	// double-quote start/stop index array
	dqarr := []int{}

	// round 1: handle trx chars
	tks := make([]uint8, 0)
	cursor := tkCHAR
	for _, r := range command {
		switch r {
		case '\\':
			cursor = tkTX
		case '\'':
			cursor = tkSQ
		case '"':
			cursor = tkDQ
		case ' ':
			cursor = tkSPX
		default:
			cursor = tkCHAR
		}

		tks = append(tks, cursor)
	}

	// round 2: handle single-quoted strs
	squote := false
	for i, tk := range tks {
		if squote == false {
			if tk == tkSQ && (i > 0 && tks[i-1] != tkTX || i == 0) {
				squote = true
				sqarr = []int{i}
			}
		} else {
			// util another single-quote occurs...
			if tk == tkSQ {
				squote = false
				sqarr = append(sqarr, i)

				// transcode chars from start -> stop
				for j := sqarr[0] + 1; j < sqarr[1]; j++ {
					tks[j] = tkCHAR
				}
			}
		}
	}
	// round 3: transcode tokens
	for i, tk := range tks {
		if tk == tkTX {
			if i < len(tks)-1 {
				tks[i] = tkNUL
				tks[i+1] = tkCHAR
				// last char (error handling)
			}
		}
	}

	// round 4: double-quote
	dquote := false
	for i, tk := range tks {
		if dquote == false {
			if tk == tkDQ {
				dquote = true
				dqarr = []int{i}
			}
		} else {
			if tk == tkDQ {
				dquote = false
				dqarr = append(dqarr, i)

				// transcode chars from start -> stop
				for j := dqarr[0] + 1; j < dqarr[1]; j++ {
					tks[j] = tkCHAR
				}
			}
		}
	}

	// round 5: handle tokens
	finalArgs := make([]string, 0)
	quoteFlag := tkNUL
	enterFlag := false

	argStr := make([]rune, 0)
	for i, tk := range tks {
		// change flag status
		switch tk {
		case tkDQ, tkSQ:
			if quoteFlag == tk {
				quoteFlag = tkNUL
			} else if quoteFlag == tkNUL {
				quoteFlag = tk
			} else {
				argStr = append(argStr, []rune(command)[i])
			}
		case tkSPX:
			if quoteFlag == tkNUL {
				enterFlag = true
			} else {
				argStr = append(argStr, []rune(command)[i])
			}
		case tkCHAR:
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
	if quoteFlag != tkNUL {
		msg := "non-closed single-quote"
		if quoteFlag == tkDQ {
			msg = "non-closed double-quote"
		}

		err = fmt.Errorf("Parse Error: %s", msg)
		return
	}
	if len(tks) > 0 && tks[len(tks)-1] == tkTX {
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
