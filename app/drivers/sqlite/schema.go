package sqlite

import (
	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
	// init migrations
	_ "github.com/DemoHn/obsidian-panel/app/migrations"
)

// SchemaUp - upgrade db schema
func (d *Driver) SchemaUp() error {
	return dbmigrate.Up(d.DB)
}

// SchemaDown - downgrate db schema
func (d *Driver) SchemaDown() error {
	return dbmigrate.Down(d.DB)
}
