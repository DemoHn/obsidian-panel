package dbmigrate

import (
	"fmt"
	"os"
	"path"
	"text/template"
	"time"
)

const pkgName = "github.com/DemoHn/obsidian-panel/pkg/dbmigrate"

const templateStr = `package migrations

import (
	"time"

	"github.com/jinzhu/gorm"

	"{{.PackageName}}"
)

func init() {
	dbmigrate.AddMigration("{{.FormatTime}}_{{.MigrationName}}", Up_{{.FormatTime}}, Down_{{.FormatTime}})
}

// Up_{{.FormatTime}} - migration up script
func Up_{{.FormatTime}}(db *gorm.DB) error {
	// Add Up Logic Here!
	return nil
}

// Down_{{.FormatTime}} - migration down script
func Down_{{.FormatTime}}(db *gorm.DB) error {
	// Add Down Logic Here!
	return nil
}
`

// NewTemplate - write a migration file with current timestamp to destination folder
func NewTemplate(name string, destFolder string) (string, error) {
	var err error
	var now = time.Now()

	var fmtTime = fmt.Sprintf("%02d%02d%02d%02d%02d%02d",
		now.Year(), now.Month(), now.Day(),
		now.Hour(), now.Minute(), now.Second())

	// TODO: add template string
	var tmplData = struct {
		PackageName   string
		MigrationName string
		FormatTime    string
	}{
		pkgName,
		name,
		fmtTime,
	}

	// init template
	var tmpl *template.Template
	if tmpl, err = template.New("migration_script").Parse(templateStr); err != nil {
		return "", err
	}
	// open file
	var destFile = fmt.Sprintf("%s_%s.go", fmtTime, name)
	var destFullPath = path.Join(destFolder, destFile)
	var fd *os.File
	if fd, err = os.Create(destFullPath); err != nil {
		return "", err
	}
	defer fd.Close()

	// execute template
	if err = tmpl.Execute(fd, tmplData); err != nil {
		return "", err
	}
	return destFullPath, nil
}
