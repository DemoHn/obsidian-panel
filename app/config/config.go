package config

import (
	"database/sql"
	"fmt"
)

var configData = map[string]Value{}

//  Config -
type Config struct {
	data map[string]Value
	db   *sql.DB
}

// LoadFromDB - load all from db
/**
func LoadFromDB(db *sql.DB) {

}

// Find - find config value with default one
func Find(key string) (Value, bool) {

}

// FindWithDefault - find config value with default one
func FindWithDefault(key string, defaultValue Value) Value {

}

// SetValue - set value and write it to DB
func SetValue(key string, value Value, db *sql.DB) error {

}
*/

//// helpers
// declare db related props
const (
	tableName     = "obs_config"
	insertColumns = "key, value, type_hint"
)

func writeValueToDB(db *sql.DB, key string, value Value) error {
	var stmt = fmt.Sprintf("insert into %s (%s) values (?, ?, ?)", tableName, insertColumns)

	if _, err := db.Exec(stmt, key, value.toString(), value.typeHint); err != nil {
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
