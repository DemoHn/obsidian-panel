package dbmigrate

import (
	"os"

	"github.com/jinzhu/gorm"
	// include sqlite
	_ "github.com/jinzhu/gorm/dialects/sqlite"
)

type sqlFixture struct {
	version string
	upSQL   string
	downSQL string
}

// only on *ix and for sqlite/mysql
const sqliteFile = "/tmp/dbmigrate_test_12138.sql"

var fixtures = []sqlFixture{
	sqlFixture{
		version: "01_A",
		upSQL:   "create table table_01(id integer, name string)",
		downSQL: "drop table table_01",
	},
	sqlFixture{
		version: "02_B",
		upSQL:   "create table table_02(id integer, name string)",
		downSQL: "drop table table_02",
	},
	sqlFixture{
		version: "03_C",
		upSQL:   "create table table_03(id integer, name string)",
		downSQL: "drop table table_03",
	},
}

func setup() *gorm.DB {
	db, _ := gorm.Open("sqlite3", sqliteFile)
	return db
}

func teardown(db *gorm.DB) {
	db.Close()
	os.Remove(sqliteFile)
}

func loadFixtures() {
	// clear global variable
	gMigrations = []*Migration{}
	// load fixtures
	for _, fixture := range fixtures {
		upSQL := fixture.upSQL
		downSQL := fixture.downSQL
		AddMigration(fixture.version, func(db *gorm.DB) error {
			return db.Exec(upSQL).Error
		}, func(db *gorm.DB) error {
			return db.Exec(downSQL).Error
		})
	}
}
