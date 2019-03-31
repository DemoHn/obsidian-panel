package secret

import (
	"database/sql/driver"
	"fmt"
	"testing"
	"time"

	// goblin
	. "github.com/franela/goblin"

	sqlmock "github.com/DATA-DOG/go-sqlmock"
	"github.com/DemoHn/obsidian-panel/app/drivers/sqlite"
)

type AnyTime struct{}

// Match satisfies sqlmock.Argument interface
func (a AnyTime) Match(v driver.Value) bool {
	_, ok := v.(time.Time)
	return ok
}

// TODO: add unhappy flow
func TestInsertSecretRecord(t *testing.T) {
	g := Goblin(t)
	var expMock sqlmock.Sqlmock
	var db *sqlite.Driver
	var err error
	g.Describe("insertSecretRecord()", func() {
		g.Before(func() {
			if db, expMock, err = sqlite.NewMock(); err != nil {
				g.Fail(err)
			}
		})
		g.After(func() {
			db.Close()
		})

		g.It("should insert data successfully", func() {
			var err error
			var expSecret = Secret{
				PublicKey:  []byte{1},
				PrivateKey: []byte{2},
				Algorithm:  "RS256",
				Active:     true,
			}
			expMock.ExpectExec(fmt.Sprintf("insert into %s", tableName)).
				WithArgs(
					[]byte{1},
					[]byte{2},
					"RS256",
					true,
					AnyTime{},
					AnyTime{},
				).
				// we don't care the actual value of result
				WillReturnResult(sqlmock.NewResult(1, 1))
			err = insertSecretRecord(db, &expSecret)
			// no error
			if err != nil {
				g.Fail(err)
			}
			// should expect expMock values
			err = expMock.ExpectationsWereMet()
			if err != nil {
				g.Fail(err)
			}
		})
	})

	g.Describe("findSecretByID()", func() {
		g.Before(func() {
			if db, expMock, err = sqlite.NewMock(); err != nil {
				g.Fail(err)
			}
		})
		g.After(func() {
			db.Close()
		})

		g.It("should find one record", func() {
			var err error

			var resSecret *Secret
			expMock.ExpectQuery(fmt.Sprintf("select %s from %s where id = .+", allColumns, tableName)).
				WithArgs(1).
				WillReturnRows(
					sqlmock.NewRows([]string{"public_key", "private_key", "algorithm", "active"}).
						AddRow([]byte{1}, []byte{2}, "RS256", true),
				)
			resSecret, err = findSecretByID(db, 1)
			// no error
			if err != nil {
				g.Fail(err)
			}
			// should expect expMock values
			err = expMock.ExpectationsWereMet()
			if err != nil {
				g.Fail(err)
			}
			// data matches
			g.Assert(resSecret.Algorithm).Eql("RS256")
			g.Assert(resSecret.PublicKey).Eql([]byte{1})
			g.Assert(resSecret.PrivateKey).Eql([]byte{2})
		})
	})
}
