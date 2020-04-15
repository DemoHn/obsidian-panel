package config

import (
	"database/sql"
	"fmt"
	"testing"

	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
	// init migrations
	_ "github.com/DemoHn/obsidian-panel/app/migrations"
	// import sqlite3
	_ "github.com/mattn/go-sqlite3"
)

func TestConfigDBLoad(t *testing.T) {
	// TODO: add testcase
	db, _ := sql.Open("sqlite3", "/tmp/b.db")
	// migration up
	dbmigrate.Down(db)
	if err := dbmigrate.Up(db); err != nil {
		panic(err)
	}

	// insert data
	err := writeValueToDB(db, "url.port", newInt(8080))
	if err != nil {
		panic(err)
	}
	writeValueToDB(db, "url.host", newString("Hello World"))

	// read data
	v, _ := readValueFromDB(db, "url.host")
	fmt.Println(v)

	// read all data
	vv, _ := loadConfigData(db)
	fmt.Println(vv)
}
