package dbmigrate

import (
	"io/ioutil"
	"os"
	"testing"

	"github.com/franela/goblin"
)

func Test_NewTemplate(t *testing.T) {
	g := goblin.Goblin(t)

	//var db *gorm.DB
	g.Describe("dbmigrate: NewTemplate()", func() {

		g.It("should write to tmp folder", func() {
			var filename string
			var err error
			if filename, err = NewTemplate("add_user", "/tmp"); err != nil {
				g.Fail(err)
			}

			if _, err = os.Open(filename); err != nil {
				g.Fail(err)
			}

			// assert file has content
			data, _ := ioutil.ReadFile(filename)
			g.Assert(len(data) > 0).Eql(true)
		})

		g.It("should throw error /no such folder", func() {
			var err error
			_, err = NewTemplate("add_user", "/no-such-folder")
			g.Assert(err != nil).Equal(true)
		})
	})
}
