package util

import (
	"os"
	"path/filepath"
)

// FileExists - utility to find if a file exists or not
// Notice:
func FileExists(path string) bool {
	if _, err := os.Stat(path); err != nil {
		return false
	}
	return true
}

// WriteFileNS - write to file with its directory auto created
// and file created
func WriteFileNS(path string, isAppend bool, data []byte) error {
	dir := filepath.Dir(path)
	// mkdir -p
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}
	return writeFile(path, isAppend, data)
}

// WriteFile - write file
func WriteFile(path string, isAppend bool, data []byte) error {
	return writeFile(path, isAppend, data)
}

// OpenFileNS - open file with its directory auto created
func OpenFileNS(path string, isAppend bool) (*os.File, error) {
	dir := filepath.Dir(path)
	// mkdir -p
	if err := os.MkdirAll(dir, 0755); err != nil {
		return nil, err
	}
	return openFile(path, isAppend)
}

// OpenFile -
func OpenFile(path string, isAppend bool) (*os.File, error) {
	return openFile(path, isAppend)
}

// RemoveContents -
func RemoveContents(dir string) error {
	d, err := os.Open(dir)
	if err != nil {
		return err
	}
	defer d.Close()
	names, err := d.Readdirnames(-1)
	if err != nil {
		return err
	}
	for _, name := range names {
		err = os.RemoveAll(filepath.Join(dir, name))
		if err != nil {
			return err
		}
	}
	return nil
}

// InitFileDir - initialize the parent directory of file
func InitFileDir(path string) error {
	return os.MkdirAll(filepath.Dir(path), 0755)
}

//// helpers
func openFile(path string, isAppend bool) (*os.File, error) {
	flags := os.O_RDWR | os.O_CREATE | os.O_TRUNC
	if isAppend {
		flags = os.O_RDWR | os.O_CREATE | os.O_APPEND
	}
	return os.OpenFile(path, flags, 0644)
}

func writeFile(path string, isAppend bool, data []byte) error {
	f, err := openFile(path, isAppend)
	if err != nil {
		return err
	}
	defer f.Close()
	if _, err := f.Write(data); err != nil {
		return err
	}
	return f.Sync()
}
