package proc

import (
	"database/sql"
	"fmt"
	"regexp"
	"strings"

	"github.com/DemoHn/obsidian-panel/util"
)

// all proc db handler
var (
	tableName = "proc_config"
	cols      = []string{
		"proc_sign",
		"name",
		"command",
		"directory",
		"env",
		"auto_start",
		"auto_restart",
		"protected",
		"stdout_logfile",
		"stderr_logfile",
		"max_retry",
	}

	fullCols = append([]string{"id"}, cols...)
)

// insert instance data to proc_config table
func insertToProcConfig(db *sql.DB, procInst *Instance) error {
	var keys = strings.Join(cols, ",")
	var tpls = strings.Join(util.Repeat("?", len(cols)), ",")

	var stmt = fmt.Sprintf("insert into %s (%s) values (%s)", tableName, keys, tpls)

	var args = []interface{}{
		procInst.name,
		procInst.procSign,
		procInst.command,
		procInst.directory,
		stringifyEnv(procInst.env),
		procInst.autoStart,
		procInst.autoRestart,
		procInst.protected,
		procInst.stdoutLogFile,
		procInst.stderrLogFile,
		procInst.maxRetry,
	}
	if _, err := db.Exec(stmt, args...); err != nil {
		return err
	}
	return nil
}

// full edit - edit one proc config
func editProcFonfig(db *sql.DB, id int, procInst *Instance) (sql.Result, error) {
	updateKeys := []string{}
	for _, col := range cols {
		updateKeys = append(updateKeys, fmt.Sprintf("%s = ?", col))
	}
	var stmt = fmt.Sprintf("update %s set %s where id = ?", tableName, strings.Join(updateKeys, ","))
	return db.Exec(stmt)
}

func listAllConfigs(db *sql.DB) ([]Instance, error) {
	var stmt = fmt.Sprintf("select %s from %s", strings.Join(fullCols, ","), tableName)
	insts := []Instance{}
	rows, err := db.Query(stmt)
	if err != nil {
		return nil, err
	}

	for rows.Next() {
		var inst Instance
		var strEnv string
		var args = []interface{}{
			&inst.id,
			&inst.name,
			&inst.procSign,
			&inst.command,
			&inst.directory,
			&strEnv,
			&inst.autoStart,
			&inst.autoRestart,
			&inst.protected,
			&inst.stdoutLogFile,
			&inst.stderrLogFile,
			&inst.maxRetry,
		}
		if err := rows.Scan(args...); err != nil {
			return nil, err
		}
		envMap, err := parseEnv(strEnv)
		if err != nil {
			return nil, err
		}
		inst.env = envMap

		insts = append(insts, inst)
	}
	return insts, nil
}

// format
// KEY1="VALUE01",KEY2="VALUE02"
// note:
// replace \ => \\
// replace " => \"
func stringifyEnv(env map[string]string) string {
	compacts := []string{}
	re := regexp.MustCompile(`(\\|")`)
	for k, v := range env {
		rv := re.ReplaceAllString(v, "\\$1")
		compacts = append(compacts, fmt.Sprintf("%s=\"%s\"", k, rv))
	}
	return strings.Join(compacts, ",")
}

func parseEnv(data string) (map[string]string, error) {
	final := map[string]string{}
	chars := []rune(data)

	// isWord: a-zA-Z0-9-_
	isWord := func(ch rune) bool {
		return (ch >= '0' && ch <= '9') ||
			(ch >= 'a' && ch <= 'z') ||
			(ch >= 'A' && ch <= 'Z') ||
			ch == '_' ||
			ch == '-'
	}
	var state = 0
	var key = []rune{}
	var val = []rune{}
	var startQuote = false
	var idx = 0
	for {
		if idx > len(chars)-1 {
			break
		}
		ch := chars[idx]
		switch state {
		case 0: // init
			if isWord(ch) {
				key = append(key, ch)
			} else if ch == '=' {
				state = 1
			} else {
				goto fail
			}
		case 1:
			if ch == '"' {
				if startQuote == false {
					startQuote = true
				} else {
					startQuote = false
					state = 2
				}
			} else if ch == '\\' {
				if idx < len(chars)-1 {
					if chars[idx+1] == '\\' {
						val = append(val, '\\')
						idx++
					} else if chars[idx+1] == '"' {
						val = append(val, '"')
						idx++
					} else {
						val = append(val, '\\')
					}
				} else {
					val = append(val, '\\')
				}
			} else {
				if startQuote == true {
					val = append(val, ch)
				} else {
					goto fail
				}
			}
		case 2:
			// append data to map
			final[string(key)] = string(val)
			// ...then reset
			key = []rune{}
			val = []rune{}
			if ch == ',' {
				state = 0
			} else {
				// break out
				return final, nil
			}
		}
		idx++
	}
	// push rest one
	if state == 2 {
		final[string(key)] = string(val)
	}
	return final, nil
fail:
	return nil, fmt.Errorf("parse env string error: malformed string at index: %d", idx)
}
