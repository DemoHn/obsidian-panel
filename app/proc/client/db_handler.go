package client

import (
	"database/sql"
	"fmt"
	"regexp"
	"strings"
	"time"

	"github.com/DemoHn/obsidian-panel/app/proc"
	"github.com/DemoHn/obsidian-panel/util"
)

// all proc db handler
var (
	tableName = "proc_config"
	cols      = []string{
		"name",
		"proc_sign",
		"command",
		"directory",
		"env",
		"auto_start",
		"auto_restart",
		"protected",
		"stdout_logfile",
		"stderr_logfile",
		"max_retry",
		"created_at",
		"updated_at",
	}
)

// InsertToProcConfig - insert instance data to proc_config table
func InsertToProcConfig(db *sql.DB, instReq proc.InstanceReq) error {
	var keys = strings.Join(cols, ",")
	var tpls = strings.Join(util.Repeat("?", len(cols)), ",")

	var stmt = fmt.Sprintf("insert into %s (%s) values (%s)", tableName, keys, tpls)
	var nowT = time.Now().Unix()
	var args = []interface{}{
		instReq.Name,
		instReq.ProcSign,
		instReq.Command,
		instReq.Directory,
		stringifyEnv(instReq.Env),
		true,
		instReq.AutoRestart,
		false,
		instReq.StdoutLogFile,
		instReq.StderrLogFile,
		instReq.MaxRetry,
		nowT,
		nowT,
	}
	if _, err := db.Exec(stmt, args...); err != nil {
		return err
	}
	return nil
}

// EditProcConfig - full edit - edit one proc config
func EditProcConfig(db *sql.DB, procSign string, instReq proc.InstanceReq) (sql.Result, error) {
	updateKeys := []string{}
	for _, col := range cols {
		// exclude created_at
		if col != "created_at" && col != "proc_sign" {
			updateKeys = append(updateKeys, fmt.Sprintf("%s = ?", col))
		}
	}
	var stmt = fmt.Sprintf("update %s set %s where proc_sign = ?", tableName, strings.Join(updateKeys, ","))
	var nowT = time.Now().Unix()
	var args = []interface{}{
		instReq.Name,
		instReq.Command,
		instReq.Directory,
		stringifyEnv(instReq.Env),
		true,
		instReq.AutoRestart,
		false,
		instReq.StdoutLogFile,
		instReq.StderrLogFile,
		instReq.MaxRetry,
		nowT,
		procSign,
	}
	return db.Exec(stmt, args...)
}

// ListAllConfigs -
func ListAllConfigs(db *sql.DB, page int, count int) ([]proc.InstanceRsp, error) {
	var stmt = fmt.Sprintf("select %s from %s limit ? offset ?", strings.Join(cols, ","), tableName)
	insts := []proc.InstanceRsp{}
	rows, err := db.Query(stmt, count, (page-1)*count)
	if err != nil {
		return nil, err
	}

	for rows.Next() {
		var inst proc.InstanceRsp
		var strEnv string
		var autoStart bool // TODO
		var args = []interface{}{
			&inst.Name,
			&inst.ProcSign,
			&inst.Command,
			&inst.Directory,
			&strEnv,
			&autoStart,
			&inst.AutoRestart,
			&inst.Protected,
			&inst.StdoutLogFile,
			&inst.StderrLogFile,
			&inst.MaxRetry,
			&inst.CreatedAt,
			&inst.UpdatedAt,
		}
		if err := rows.Scan(args...); err != nil {
			return nil, err
		}
		envMap, err := parseEnv(strEnv)
		if err != nil {
			return nil, err
		}
		inst.Env = envMap

		insts = append(insts, inst)
	}
	return insts, nil
}

// CountTotalList -
func CountTotalList(db *sql.DB) (int, error) {
	var count int
	if err := db.QueryRow(fmt.Sprintf("select count(*) from %s", tableName)).Scan(&count); err != nil {
		return 0, err
	}
	return count, nil
}

// GetProcConfig -
func GetProcConfig(db *sql.DB, procSign string) (proc.InstanceRsp, error) {
	var stmt = fmt.Sprintf("select %s from %s where proc_sign = ?", strings.Join(cols, ","), tableName)

	var inst proc.InstanceRsp
	var strEnv string
	var autoStart bool // TODO
	var args = []interface{}{
		&inst.Name,
		&inst.ProcSign,
		&inst.Command,
		&inst.Directory,
		&strEnv,
		&autoStart,
		&inst.AutoRestart,
		&inst.Protected,
		&inst.StdoutLogFile,
		&inst.StderrLogFile,
		&inst.MaxRetry,
		&inst.CreatedAt,
		&inst.UpdatedAt,
	}
	if err := db.QueryRow(stmt, procSign).Scan(args...); err != nil {
		return proc.InstanceRsp{}, err
	}

	envMap, err := parseEnv(strEnv)
	if err != nil {
		return proc.InstanceRsp{}, err
	}
	inst.Env = envMap

	return inst, nil
}

// InsertSysProcess - insert system process that should be registered by default
func InsertSysProcess(db *sql.DB) error {
	defaultInsts := []proc.InstanceReq{
		{
			Name:        "API server",
			ProcSign:    "sys-api-server",
			Command:     "./obs sys:proc api-server",
			Env:         map[string]string{},
			AutoRestart: true,
			MaxRetry:    9999, // TODO: set unlimited int the future
		},
	}

	for _, inst := range defaultInsts {
		if err := InsertToProcConfig(db, inst); err != nil {
			return err
		}
	}
	return nil
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
