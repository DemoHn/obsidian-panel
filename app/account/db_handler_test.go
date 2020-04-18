package account

import (
	"database/sql"
	"fmt"
	"os"
	"reflect"
	"testing"

	"github.com/AlekSi/pointer"
	"github.com/DemoHn/obsidian-panel/app/drivers/sqlite"
)

const sqliteFile = "/tmp/account_repo_test_1984.sql"

// add example data
var allAccountsForInsert = []Account{}
var allAccounts = []Account{}

func init() {
	for i := 1; i <= 10; i++ {
		acct := Account{
			ID:         i,
			Name:       fmt.Sprintf("%v.admin@g.com", i),
			Credential: []byte{1, 2},
			PermLevel:  USER,
		}
		allAccountsForInsert = append(allAccountsForInsert, acct)
		acct.Credential = nil
		allAccounts = append(allAccounts, acct)
	}
}

func setup(t *testing.T) *sql.DB {
	db, _ := sql.Open("sqlite3", sqliteFile)
	if err := db.SchemaUp(); err != nil {
		t.Errorf("%v", err)
		return nil
	}
	return db
}

func clear(db *sqlite.Driver) {
	db.Exec("delete from accounts")
	db.Exec("delete from sqlite_sequence where name = 'accounts'")
}

func teardown(db *sqlite.Driver) {
	db.Close()
	os.Remove(sqliteFile)
}

func Test_insertAccountRecord(t *testing.T) {
	// setup & teardown
	var gDB = setup(t)
	defer teardown(gDB)

	type args struct {
		account *Account
	}
	tests := []struct {
		name    string
		args    args
		wantErr bool
	}{
		{
			name: "insert account data",
			args: args{
				account: &Account{
					Name:       "admin@g.com",
					PermLevel:  ADMIN,
					Credential: []byte{1, 2, 3},
				},
			},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if err := insertAccountRecord(gDB, tt.args.account); (err != nil) != tt.wantErr {
				t.Errorf("insertAccountRecord() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}

func Test_listAccountsRecord(t *testing.T) {
	var err error
	// setup & teardown
	var gDB = setup(t)
	// clear accounts
	clear(gDB)

	for i := 0; i < 10; i++ {
		err = insertAccountRecord(gDB, &allAccountsForInsert[i])
		if err != nil {
			t.Errorf("%v", err)
		}
	}

	// construct args
	type args struct {
		db     *sqlite.Driver
		filter AccountsFilter
	}
	tests := []struct {
		name    string
		args    args
		want    []Account
		wantErr bool
	}{
		{
			name: "list all account",
			args: args{
				db:     gDB,
				filter: AccountsFilter{},
			},
			want:    allAccounts,
			wantErr: false,
		},
		{
			name: "list with nameLike",
			args: args{
				db: gDB,
				filter: AccountsFilter{
					nameLike: pointer.ToString("1%"),
				},
			},
			want:    []Account{allAccounts[0], allAccounts[9]},
			wantErr: false,
		},
		{
			name: "list with offset & limit",
			args: args{
				db: gDB,
				filter: AccountsFilter{
					limit:  pointer.ToInt(3),
					offset: pointer.ToInt(4),
				},
			},
			want:    []Account{allAccounts[4], allAccounts[5], allAccounts[6]},
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := listAccountsRecord(tt.args.db, tt.args.filter)
			if (err != nil) != tt.wantErr {
				t.Errorf("listAccountsRecord() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("listAccountsRecord() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_getAccountByName(t *testing.T) {
	// insert DB
	var gDB = setup(t)

	type args struct {
		db   *sqlite.Driver
		name string
	}
	tests := []struct {
		name    string
		args    args
		want    *Account
		wantErr bool
	}{
		{
			name: "find one account",
			args: args{
				db:   gDB,
				name: "1.admin@g.com",
			},
			want: &Account{
				ID:         1,
				PermLevel:  USER,
				Credential: []byte{1, 2},
				Name:       "1.admin@g.com",
			},
			wantErr: false,
		},
		{
			name: "should not find any account",
			args: args{
				db:   gDB,
				name: "NOT_FOUND@g.com",
			},
			want:    nil,
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := getAccountByName(tt.args.db, tt.args.name)
			if (err != nil) != tt.wantErr {
				t.Errorf("getAccountByName() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("getAccountByName() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_countTotalAccounts(t *testing.T) {
	// insert DB
	var gDB = setup(t)
	defer teardown(gDB)

	type args struct {
		db *sqlite.Driver
	}
	tests := []struct {
		name    string
		args    args
		want    int
		wantErr bool
	}{
		{
			name: "get total number",
			args: args{
				db: gDB,
			},
			want:    10, // since previously there're 10 accounts existing
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := countTotalAccounts(tt.args.db)
			if (err != nil) != tt.wantErr {
				t.Errorf("countTotalAccounts() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("countTotalAccounts() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_changePermission(t *testing.T) {
	// insert DB
	var gDB = setup(t)
	defer teardown(gDB)

	type args struct {
		db      *sqlite.Driver
		acct    *Account
		newPerm PermLevel
	}
	tests := []struct {
		name    string
		args    args
		want    *Account
		wantErr bool
	}{
		{
			name: "should change permission -> ADMIN",
			args: args{
				db:      gDB,
				acct:    &allAccounts[1],
				newPerm: ADMIN,
			},
			want:    &allAccounts[1],
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := changePermission(tt.args.db, tt.args.acct, tt.args.newPerm)
			if (err != nil) != tt.wantErr {
				t.Errorf("changePermission() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("changePermission() = %v, want %v", got, tt.want)
			}
		})
	}
}

func Test_changeCredential(t *testing.T) {
	// insert DB
	var gDB = setup(t)
	defer teardown(gDB)

	type args struct {
		db         *sqlite.Driver
		acct       *Account
		credential []byte
	}
	tests := []struct {
		name    string
		args    args
		want    *Account
		wantErr bool
	}{
		{
			name: "should change credential",
			args: args{
				db:         gDB,
				acct:       &allAccounts[1],
				credential: []byte{2, 3},
			},
			want:    &allAccounts[1],
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := changeCredential(tt.args.db, tt.args.acct, tt.args.credential)
			if (err != nil) != tt.wantErr {
				t.Errorf("changeCredential() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("changeCredential() = %v, want %v", got, tt.want)
			}
		})
	}
}
