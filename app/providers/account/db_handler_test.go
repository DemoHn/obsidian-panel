package account

import (
	"fmt"
	"os"
	"testing"

	"github.com/DemoHn/obsidian-panel/app/drivers/sqlite"

	"github.com/DemoHn/obsidian-panel/infra"

	// goblin
	. "github.com/franela/goblin"
)

const sqliteFile = "/tmp/account_repo_test_1984.sql"

func setup() *sqlite.Driver {
	db, _ := sqlite.NewForTest(sqliteFile)
	return db
}

func clear(db *sqlite.Driver) {
	db.Exec("delete from accounts")
}

func teardown(db *sqlite.Driver) {
	db.Close()
	os.Remove(sqliteFile)
}

func TestAccountRepo(t *testing.T) {
	g := Goblin(t)

	var db *sqlite.Driver

	g.Describe("account database", func() {
		g.Before(func() {
			db = setup()
			db.SchemaUp()
		})

		g.After(func() {
			db.SchemaDown()
			// delete sqlite file resolves everything!
			teardown(db)
		})

		g.It("should insert account data", func() {
			expAdmin := "admin@g.com"
			expCredential := []byte{1, 2, 3}
			expPermLevel := ADMIN

			err := insertAccountRecord(db, &Account{
				Name:       expAdmin,
				PermLevel:  expPermLevel,
				Credential: expCredential,
			})
			if err != nil {
				g.Fail(err)
			}
		})

		g.It("should list all accounts", func() {
			var err error
			// delete previous data
			clear(db)
			// insert more accounts
			for i := 0; i < 10; i++ {
				err = insertAccountRecord(db, &Account{
					Name:       fmt.Sprintf("%v.admin@g.com", i),
					Credential: []byte{1, 2},
					PermLevel:  USER,
				})

				if err != nil {
					g.Fail(err)
				}
			}

			// list all data
			var accts []Account
			if accts, err = listAccountsRecord(db, nil, nil); err != nil {
				g.Fail(err)
			}
			g.Assert(len(accts)).Equal(10)

			// list with offset & limit
			var limit = 3
			var offsetA = 4
			if accts, err = listAccountsRecord(db, &limit, &offsetA); err != nil {
				g.Fail(err)
			}
			g.Assert(len(accts)).Equal(3)
			g.Assert(accts[0].Name).Equal("4.admin@g.com")
		})

		g.It("should find one account", func() {
			expUser := "1.admin@g.com"
			acct, err := getAccountByName(db, expUser)
			if err != nil {
				g.Fail(err)
			}

			g.Assert(acct.Name).Equal(expUser)
			g.Assert(acct.PermLevel).Equal(USER)
		})

		g.It("should throw error", func() {
			expUser := "notFoundUser"

			_, err := getAccountByName(db, expUser)
			// assert type
			e, typeOK := err.(*infra.Error)
			if !typeOK {
				g.Fail("incorrect type")
			}

			g.Assert(e.Name).Equal("FindAccountError")
		})
	})
}
