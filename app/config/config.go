package config

import (
	"database/sql"
	"fmt"
	"strings"
)

var configData = map[string]Value{}

//  Config -
type Config struct {
	data map[string]Value
	db   *sql.DB
}

// New -
func New(db *sql.DB) *Config {
	return &Config{
		data: map[string]Value{},
		db:   db,
	}
}

// Load all data from db, and append defaults if possible
func (config *Config) Load() error {
	// I. load from DB
	initVal, err := loadConfigData(config.db)
	if err != nil {
		return err
	}
	config.data = initVal
	// II. check with defaults
	var pendingInsertMap = map[string]Value{}
	for k, v := range defaults {
		if _, ok := config.data[k]; !ok {
			pendingInsertMap[k] = v
		}
	}

	// III. write data if exists
	if len(pendingInsertMap) > 0 {
		return bulkInsertToDB(config.db, pendingInsertMap)
	}
	return nil
}

// Find - find value by key
func (config *Config) Find(key string) (Value, error) {
	// I. first, try to find data from data cache
	v, ok := config.data[key]
	if ok {
		return v, nil
	}
	// II. then try to read from db
	return readValueFromDB(config.db, key)
}

// Set - set data
func (config *Config) Set(key string, value Value) error {
	// I. write to DB first
	if err := writeValueToDB(config.db, key, value); err != nil {
		return err
	}
	// II. write back to config
	config.data[key] = value
	return nil
}

//// helpers
// declare db related props
const (
	tableName     = "obs_config"
	insertColumns = "key, value, type_hint"
)

func writeValueToDB(db *sql.DB, key string, value Value) error {
	var insertStmt = fmt.Sprintf("insert into %s (%s) values (?, ?, ?)", tableName, insertColumns)
	var selectStmt = fmt.Sprintf("select value from %s where key = ?", tableName)
	var updateStmt = fmt.Sprintf("update %s set value = ? where key = ?", tableName)
	var pValue string

	// I. find data
	if err := db.QueryRow(selectStmt, key).Scan(&pValue); err != nil {
		if err == sql.ErrNoRows {
			// insert
			if _, err := db.Exec(insertStmt, key, value.toString(), value.typeHint); err != nil {
				return err
			}
			return nil
		}
		return err
	}
	// II. updated data is some, no need to update db again
	if pValue != value.toString() {
		if _, err := db.Query(updateStmt, value.toString(), key); err != nil {
			return err
		}
	}
	return nil
}

func bulkInsertToDB(db *sql.DB, data map[string]Value) error {
	var valStrs = []string{}
	var valArgs = []interface{}{}

	for k, v := range data {
		valStrs = append(valStrs, "(?, ?, ?)")
		valArgs = append(valArgs, k, v.toString(), v.typeHint)
	}

	var stmt = fmt.Sprintf("insert into %s (%s) values %s", tableName, insertColumns, strings.Join(valStrs, ","))
	if _, err := db.Exec(stmt, valArgs...); err != nil {
		return err
	}
	return nil
}

func readValueFromDB(db *sql.DB, key string) (Value, error) {
	var stmt = fmt.Sprintf("select value, type_hint from %s where key = ?", tableName)
	var valueStr string
	var typeHint int
	if err := db.QueryRow(stmt, key).Scan(&valueStr, &typeHint); err != nil {
		if err == sql.ErrNoRows {
			return Value{}, err
		}
		return Value{}, err
	}

	return newFromString(valueStr, typeHint), nil
}

func loadConfigData(db *sql.DB) (map[string]Value, error) {
	var configMap = map[string]Value{}
	var stmt = fmt.Sprintf("select %s from %s", insertColumns, tableName)
	rows, err := db.Query(stmt)
	if err != nil {
		return nil, err
	}
	for rows.Next() {
		var key string
		var valueStr string
		var typeHint int
		if err := rows.Scan(&key, &valueStr, &typeHint); err != nil {
			return nil, err
		}
		configMap[key] = newFromString(valueStr, typeHint)
	}
	return configMap, nil
}
