package gorm

import (
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/jinzhu/gorm"
)

// Driver - gorm_driver is a wrapper of the popular ORM: gorm
type Driver struct {
	DB *gorm.DB
}

// NewDriver - new gorm driver
func NewDriver(infra *infra.Infrastructure) (*Driver, error) {
	var err error
	var db *gorm.DB
	var dbURL string

	// find dbURL first
	if dbURL, err = GenerateDatabaseURL(infra); err != nil {
		return nil, err
	}

	// open db connection
	if db, err = gorm.Open("mysql", dbURL); err != nil {
		return nil, err
	}

	return &Driver{DB: db}, nil
}

func (d *Driver) Error() error {
	return d.DB.Error
}

// THE FOLLOWING FUNCTIONS ARE ALL FROM gorm.DB WITH SAME SIGNATURE
// TODO: use code generator to automatically get it

// Begin - begin an transaction
func (d *Driver) Begin() *Driver {
	d.DB = d.DB.Begin()
	return d
}

// Commit - commit an transaction
func (d *Driver) Commit() *Driver {
	d.DB = d.DB.Commit()
	return d
}

// Rollback - rollback an transaction
func (d *Driver) Rollback() *Driver {
	d.DB = d.DB.Rollback()
	return d
}

// migration

// AutoMigrate - auto migrate data
func (d *Driver) AutoMigrate(values ...interface{}) *Driver {
	d.DB = d.DB.AutoMigrate(values...)
	return d
}

// query

// Create - create record
func (d *Driver) Create(value interface{}) *Driver {
	d.DB = d.DB.Create(value)
	return d
}

// Find -
func (d *Driver) Find(out interface{}, where ...interface{}) *Driver {
	d.DB = d.DB.Find(out, where...)
	return d
}

// Limit - add limitation of query
func (d *Driver) Limit(limit interface{}) *Driver {
	d.DB = d.DB.Limit(limit)
	return d
}

// Offset - add offset of query
func (d *Driver) Offset(offset interface{}) *Driver {
	d.DB = d.DB.Offset(offset)
	return d
}

// Where - where conditions
func (d *Driver) Where(query interface{}, args ...interface{}) *Driver {
	d.DB = d.DB.Where(query, args...)
	return d
}

// Order - order the query
func (d *Driver) Order(value interface{}, reorder ...bool) *Driver {
	d.DB = d.DB.Order(value, reorder...)
	return d
}

// Update -
func (d *Driver) Update(attrs ...interface{}) *Driver {
	d.DB = d.DB.Update(attrs...)
	return d
}

// Delete -
func (d *Driver) Delete(value interface{}, where ...interface{}) *Driver {
	d.DB = d.DB.Delete(value, where...)
	return d
}

// First -
func (d *Driver) First(out interface{}, where ...interface{}) *Driver {
	d.DB = d.DB.First(out, where...)
	return d
}

// Model -
func (d *Driver) Model(value interface{}) *Driver {
	d.DB = d.DB.Model(value)
	return d
}

// Save -
func (d *Driver) Save(value interface{}) *Driver {
	d.DB = d.DB.Save(value)
	return d
}

// misc

// Debug -
func (d *Driver) Debug() *Driver {
	d.DB = d.DB.Debug()
	return d
}

// Close - close DB
func (d *Driver) Close() error {
	return d.DB.Close()
}
