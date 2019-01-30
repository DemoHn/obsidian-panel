package main

import (
	"fmt"
	"os"

	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
)

func main() {
	args := os.Args

	if len(args) > 1 {
		if args[1] == "migrate:new" {
			if _, err := dbmigrate.NewTemplate(args[2], "app/migrations"); err != nil {
				panic(err)
			}
		}
	}

	fmt.Println("CLI execution finish")
}
