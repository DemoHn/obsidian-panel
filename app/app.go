package app

import (
	"database/sql"
	"fmt"
	"os"

	"github.com/DemoHn/obsidian-panel/app/account"
	"github.com/DemoHn/obsidian-panel/app/config"
	"github.com/DemoHn/obsidian-panel/app/proc"
	procClient "github.com/DemoHn/obsidian-panel/app/proc/client"
	"github.com/DemoHn/obsidian-panel/app/sqlc"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/DemoHn/obsidian-panel/util"
)

// declare input params
var (
	rootPath string // if empty, use default one
	debug    bool   // enter debug mode
)

const (
	dtUser     = "admin"     // default admin user
	dtPassword = "0bs-pane1" // deafult admin password
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
	path, err := util.FindRootPath(rootPath)
	if err != nil {
		return nil, err
	}
	// II. init dirs
	if err := initDirs(path); err != nil {
		return nil, err
	}
	// III. open db
	db, err := FindRootDB(path)
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

// GetConfig -
func (ap *App) GetConfig() *config.Config {
	return ap.cfg
}

// GetDB -
func (ap *App) GetDB() *sql.DB {
	return ap.db
}

// GetRootPath -
func (ap *App) GetRootPath() string {
	return ap.rootPath
}

// Start - start app
func Start(app *App, foreground bool) error {
	infra.SetMainLoggerLevel(app.debug)
	// I. migrate up
	infra.Log.Info("establish db schema...")
	needInit, err := sqlc.MigrateInit(app.db)
	if err != nil {
		return err
	}
	// II. Load config
	infra.Log.Info("load config...")
	if err := app.cfg.Load(); err != nil {
		return err
	}

	if needInit {
		// III. inject default data
		if err := account.RegisterAdminNS(app.db, dtUser, dtPassword); err != nil {
			return err
		}
		if err := procClient.InsertSysProcess(app.db); err != nil {
			return err
		}
	}

	if err := proc.StartDaemon(app.rootPath, app.debug, foreground); err != nil {
		return err
	}
	if !foreground {
		return loadAndStartSysProc(app.rootPath, app.db)
	}
	return nil
}

// Stop -
func Stop(app *App) error {
	infra.SetMainLoggerLevel(app.debug)
	// I.
	infra.Log.Info("going to kill panel daemon...")
	return proc.KillDaemon(app.rootPath)
}

// FindRootDB -
func FindRootDB(rootPath string) (*sql.DB, error) {
	path, err := util.FindRootPath(rootPath)
	if err != nil {
		return nil, err
	}
	sqlFile := fmt.Sprintf("%s/sql/root.db", path)
	return sqlc.OpenDB(sqlFile)
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

func loadAndStartSysProc(rootPath string, db *sql.DB) error {
	var out1 proc.DataRsp
	var out2 proc.StartRsp
	insts, err := procClient.ListAllConfigs(db, 0, 0)
	if err != nil {
		return err
	}

	instReqs := []proc.InstanceReq{}
	// transform instRsp -> instReq
	for _, ist := range insts {
		instReqs = append(instReqs, proc.InstanceReq{
			ProcSign:      ist.ProcSign,
			Name:          ist.Name,
			Command:       ist.Command,
			Directory:     ist.Directory,
			Env:           ist.Env,
			AutoRestart:   ist.AutoRestart,
			StdoutLogFile: ist.StdoutLogFile,
			StderrLogFile: ist.StderrLogFile,
			MaxRetry:      ist.MaxRetry,
		})
	}
	// load all config
	if err := procClient.SendRequest(rootPath, "Master.LoadConfig", instReqs, &out1); err != nil {
		return err
	}
	// start sys-api-server
	// TODO: more decent way to manage sys process
	if err := procClient.SendRequest(rootPath, "Master.Start", "sys-api-server", &out2); err != nil {
		return err
	}
	infra.Log.Info("start api-server success")
	return nil
}
