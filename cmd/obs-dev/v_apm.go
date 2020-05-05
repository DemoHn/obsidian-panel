package main

import (
	"crypto/rand"
	"fmt"
	"os"
	"os/signal"
	"time"

	"github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

var (
	printEnv  bool
	exitAfter int
	writeRAM  int
)

var apmCmd = &cobra.Command{
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

func init() {
	apmCmd.Flags().BoolVar(&printEnv, "printEnv", false, "print current env")
	apmCmd.Flags().IntVar(&exitAfter, "exitAfter", 0, "assign exit after (N) seconds, 0 for never exit")
	apmCmd.Flags().IntVar(&writeRAM, "writeRAM", 0, "write (N)M RAM (for testing pidusage)")
}

func writeRAMWorker(block []byte, num int) {
	block = make([]byte, num)
	_, err := rand.Read(block)
	if err != nil {
		fmt.Println(err)
	}
}
