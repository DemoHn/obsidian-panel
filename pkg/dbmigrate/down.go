package dbmigrate

import (
	"fmt"

	"github.com/jinzhu/gorm"
)

// Down - down to lowest version
func Down(db *gorm.DB) error {
	var err error
	if err = initMigrationTable(db); err != nil {
		return fmt.Errorf("init migration table failed: %s", err.Error())
	}

	var versions []string
	if versions, err = readMigrationTable(db, false); err != nil {
		return fmt.Errorf("read migration table failed: %s", err.Error())
	}

	execMigrations := filterMigrations(versions, gMigrations, false)
	// no need to order since `versions` are naturally ordered
	if err = downMigrations(db, execMigrations); err != nil {
		return err
	}
	return nil
}

func downMigrations(db *gorm.DB, migrations []*Migration) error {
	var err error
	for _, mg := range migrations {
		err = transaction(db, func(tx *gorm.DB) error {
			var e error
			if e = mg.Down(db); e != nil {
				return e
			}
			// add item to migration_history
			if e = db.Delete(&MigrationHistory{Version: mg.Version}).Error; e != nil {
				return e
			}
			return nil
		})

		if err != nil {
			return fmt.Errorf("migration error on version[%s]: %s", mg.Version, err.Error())
		}
	}

	return nil
}
