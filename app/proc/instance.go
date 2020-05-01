package proc

// Instance - a basic unit of process management
type Instance struct {
	id          int
	name        string
	procSign    string
	command     string
	directory   string
	env         map[string]string
	autoStart   bool
	autoRestart bool
	// protected - could not be edited by users
	// ususally for system process
	protected     bool
	maxRetry      int
	stdoutLogFile string
	stderrLogFile string
}
