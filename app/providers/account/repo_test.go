//go:generate mockgen -self_package=github.com/DemoHn/obsidian-panel/app/providers/account -destination=repo_mock.go -package=account -source=repo.go Repository
//go:generate sed -i "" "s/*x./*/g;s/ x./ /g;s/]x./]/g;/x \".\"/d" repo_mock.go
package account

import (
	"fmt"
	"os"
	"testing"

	dGorm "github.com/DemoHn/obsidian-panel/app/drivers/gorm"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/jinzhu/gorm"

	// goblin
	. "github.com/franela/goblin"
)

const sqliteFile = "/tmp/account_repo_test_1984.sql"

func setup() *gorm.DB {
	db, _ := gorm.Open("sqlite3", sqliteFile)
	return db
}

func clear(db *gorm.DB) {
	db.Delete(Model{})
}

func teardown(db *gorm.DB) {
	db.Close()
	os.Remove(sqliteFile)
}

func TestAccountRepo(t *testing.T) {
	g := Goblin(t)

	var db *gorm.DB
	var drv *dGorm.Driver
	var ar *repository

	g.Describe("accountRepo", func() {
		g.Before(func() {
			db = setup()
			drv = &dGorm.Driver{
				DB: db,
			}
			drv.SchemaUp()
			// init provider
			ar = &repository{drv}
		})

		g.After(func() {
			drv.SchemaDown()
			// delete sqlite file resolves everything!
			teardown(db)
		})

		g.It("should insert account data", func() {
			expAdmin := "admin@g.com"
			expCredential := []byte{1, 2, 3}
			expPermLevel := ADMIN

			acct, err := ar.InsertAccountData(expAdmin, expCredential, expPermLevel)
			if err != nil {
				g.Fail(err)
			}

			g.Assert(acct.Name).Equal(expAdmin)
			g.Assert(acct.Credential).Equal(expCredential)
			g.Assert(acct.PermLevel).Equal(expPermLevel)
		})

		g.It("should list all accounts", func() {
			var err error
			// delete previous data
			clear(db)
			// insert more accounts
			for i := 0; i < 10; i++ {
				_, err = ar.InsertAccountData(fmt.Sprintf("%v.admin@g.com", i), []byte{1, 2}, USER)
				if err != nil {
					g.Fail(err)
				}
			}

			// list all data
			var accts []Model
			if accts, err = ar.ListAccountsData(nil, nil); err != nil {
				g.Fail(err)
			}
			g.Assert(len(accts)).Equal(10)

			// list with offset & limit
			var limit = 3
			var offsetA = 4
			if accts, err = ar.ListAccountsData(&limit, &offsetA); err != nil {
				g.Fail(err)
			}
			g.Assert(len(accts)).Equal(3)
			g.Assert(accts[0].Name).Equal("4.admin@g.com")
		})

		g.It("should find one account", func() {
			expUser := "1.admin@g.com"
			acct, err := ar.GetAccountByName(expUser)
			if err != nil {
				g.Fail(err)
			}

			g.Assert(acct.Name).Equal(expUser)
			g.Assert(acct.PermLevel).Equal(USER)
		})

		g.It("should throw error", func() {
			expUser := "notFoundUser"

			_, err := ar.GetAccountByName(expUser)
			// assert type
			e, typeOK := err.(*infra.Error)
			if !typeOK {
				g.Fail("incorrect type")
			}

			g.Assert(e.Name).Equal("FindAccountError")
		})
	})
}
