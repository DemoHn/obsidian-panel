package app

import (
	"database/sql"
	"fmt"
	"os"

	"github.com/DemoHn/obsidian-panel/app/api"
	"github.com/DemoHn/obsidian-panel/app/config"
)

// declare input params
var (
	rootPath string // if empty, use default one
	debug    bool   // enter debug mode
)

// App - new app data
type App struct {
	rootPath string
	debug    bool
	db       *sql.DB
	cfg      *config.Config
}

// New - new appInstance
func New(rootPath string, debug bool) (*App, error) {
	// I. get root path
	path, err := findRootPath(rootPath)
	if err != nil {
		return nil, err
	}
	// II. init dirs
	if err := initDirs(path); err != nil {
		return nil, err
	}
	// III. open db
	db, err := findRootDB(path)
	if err != nil {
		return nil, err
	}
	return &App{
		rootPath: path,
		debug:    debug,
		db:       db,
		cfg:      config.New(db),
	}, nil
}

// Start - start app
func Start(app *App) error {
	return api.StartServer(app.cfg, app.db)
}

// FindRootDB -
func FindRootDB(rootPath string) (*sql.DB, error) {
	return findRootDB(rootPath)
}

//// helpers
func findRootPath(rootPath string) (string, error) {
	// priority:
	// 1. $rootPath
	// 2. $HOME/.obs-root

	// if rootPath is not empty, the directory must exists!
	if rootPath != "" {
		if _, err := os.Stat(rootPath); err != nil {
			return "", err
		}
	} else {
		// read $HOME
		home, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		homePath := fmt.Sprintf("%s/.obs-root", home)
		if err := os.MkdirAll(homePath, os.ModePerm); err != nil {
			return "", err
		}
		rootPath = homePath
	}
	return rootPath, nil
}

func initDirs(rootPath string) error {
	var dirs = []string{
		"sql", "log", "data", "proc",
	}
	for _, dir := range dirs {
		path := fmt.Sprintf("%s/%s", rootPath, dir)
		if err := os.MkdirAll(path, os.ModePerm); err != nil {
			return err
		}
	}
	return nil
}

func findRootDB(rootPath string) (*sql.DB, error) {
	const (
		sqlPathFmt = "%s/sql"
		sqlFileFmt = "%s/sql/root.db"
	)
	// 1. $rootPath
	// 2. $HOME/.obs-root/sql/root.db
	//
	// An error will be thrown if both locations are not found.

	// I. first try to open DB from predefined dbFile
	if rootPath == "" {
		home, err := os.UserHomeDir()
		if err != nil {
			return nil, err
		}
		rootPath = fmt.Sprintf(sqlPathFmt, home)
	}

	// ensure rootPath exists
	if _, err := os.Stat(rootPath); err != nil {
		return nil, err
	}
	// then open db directly
	return sql.Open("sqlite3", fmt.Sprintf(sqlFileFmt, rootPath))
}
