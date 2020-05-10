package main

import (
	"crypto/rand"
	"fmt"
	"os"
	"os/signal"
	"time"

	"net/rpc"

	"github.com/DemoHn/obsidian-panel/app/proc"
	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

var (
	printEnv  bool
	exitAfter int
	writeRAM  int
	sockFile  string
)

var apmProcCmd = &cobra.Command{
	Use:   "apm:proc",
	Short: "example proc, used for testing spawn processes",
	Run: func(cmd *cobra.Command, args []string) {
		var block []byte

		log := logrus.New()
		log.SetFormatter(&logrus.TextFormatter{
			FullTimestamp:          true,
			DisableLevelTruncation: true,
			// <year>-<month>-<date> <Hour>:<minute>:<second>
			TimestampFormat: "2006-01-02 15:04:05",
		})
		log.Info("=========================")
		log.Info("process started...")

		if printEnv {
			for _, ev := range os.Environ() {
				fmt.Println(ev)
			}
		}

		var sig = make(chan os.Signal, 1)
		signal.Notify(sig, os.Interrupt)

		// do some work
		if writeRAM > 0 {
			go writeRAMWorker(block, writeRAM*1024*1024)
		}

		if exitAfter == 0 {
			select {
			case <-sig:
				log.Info("receive signal, going to exit...")
			}
		} else {
			select {
			case <-sig:
				log.Info("receive signal, going to exit...")
			case <-time.After(time.Duration(exitAfter) * time.Second):
				log.Infof("after %d seconds, the process will exit normally", exitAfter)
			}
		}
		log.Info("-------------------------")
	},
}

var apmCtrlCmd = &cobra.Command{
	Use:   "apm:ctrl",
	Short: "send ctrl commands to daemon process valid command:sync,start",
	Args:  cobra.MinimumNArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		var sock = sockFile
		if sockFile == "" {
			home, _ := os.UserHomeDir()
			sock = fmt.Sprintf("%s/.obs-root/proc/obs-daemon.sock", home)
		}

		client, err := rpc.DialHTTP("unix", sock)
		if err != nil {
			panic(err)
		}
		switch args[0] {
		case "start":
			var rsp proc.StartRsp
			var procSign = "proc1"
			if len(args) > 1 {
				procSign = args[1]
			}

			if err := client.Call("Master.Start", procSign, &rsp); err != nil {
				panic(err)
			}
			fmt.Println("rsp:", rsp)
		case "restart":
			var rsp proc.StartRsp
			var procSign = "proc1"
			if len(args) > 1 {
				procSign = args[1]
			}

			if err := client.Call("Master.Restart", procSign, &rsp); err != nil {
				panic(err)
			}
			fmt.Println("rsp:", rsp)
		case "stop":
			var rsp proc.StopRsp
			var procSign = "proc1"
			if len(args) > 1 {
				procSign = args[1]
			}

			if err := client.Call("Master.Stop", procSign, &rsp); err != nil {
				panic(err)
			}
			fmt.Println("rsp:", rsp)
		case "sync":
			var rsp proc.DataRsp
			// sync with example data
			exampleData := []proc.InstanceReq{
				{
					ProcSign:      "proc1",
					Name:          "example hello",
					Command:       "./obs-dev apm:proc --printEnv",
					Directory:     "",
					Env:           map[string]string{},
					AutoStart:     true,
					AutoRestart:   true,
					StdoutLogFile: "$rootPath/$procSign.log",
					StderrLogFile: "$rootPath/$procSign.log",
					MaxRetry:      3,
				},
			}
			if err := client.Call("Master.Sync", &exampleData, &rsp); err != nil {
				panic(err)
			}
			fmt.Println("rsp:", rsp)
		case "echo":
			var reply string
			var input = "ping"
			if len(args) > 1 {
				input = args[1]
			}
			err := client.Call("Master.Echo", &input, &reply)
			if err != nil {
				panic(err)
			}
			fmt.Printf("echo: %s\n", reply)
		}
	},
}

func init() {
	apmProcCmd.Flags().BoolVar(&printEnv, "printEnv", false, "print current env")
	apmProcCmd.Flags().IntVar(&exitAfter, "exitAfter", 0, "assign exit after (N) seconds, 0 for never exit")
	apmProcCmd.Flags().IntVar(&writeRAM, "writeRAM", 0, "write (N)M RAM (for testing pidusage)")

	apmCtrlCmd.Flags().StringVar(&sockFile, "sockFile", "", "daemon connection socket file")
}

func writeRAMWorker(block []byte, num int) {
	block = make([]byte, num)
	_, err := rand.Read(block)
	if err != nil {
		fmt.Println(err)
	}
}
