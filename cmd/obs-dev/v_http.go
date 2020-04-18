package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strings"

	"github.com/AlecAivazis/survey/v2"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var (
	tokenFile string
	host      string
	port      int
)

// Example Command:
// obs-dev http:get /api/v1/accounts -h 127.0.0.1 -p 12138 --qs hello=1,world=2
var httpGetCmd = &cobra.Command{
	Use:   "http:get",
	Short: "Send HTTP GET request to panel; usually for testing",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		var promptName = &survey.Input{
			Message: "Login as:",
		}

		var promptPassword = &survey.Password{
			Message: "Password:",
		}
		var name string
		var password string
		qs, _ := viper.Get("qs").([]string)
		// I. do get
		res, err := doGet(host, port, args[0], qs)
		if err != nil {
			return err
		}
		if !res {
			survey.AskOne(promptName, &name)
			survey.AskOne(promptPassword, &password)

			// II. do get again
			_, err := doGet(host, port, args[0], qs)
			if err != nil {
				return err
			}
		}
		return nil
	},
}

func doGet(host string, port int, url string, qs []string) (bool, error) {
	qss := strings.Join(qs, "&")
	endpoint := fmt.Sprintf("http://%s:%d/%s?%s", host, port, url, qss)

	client := new(http.Client)
	req, _ := http.NewRequest("GET", endpoint, nil)
	req.Header.Set("Content-Type", "application/json")
	// read data
	tk, _ := ioutil.ReadFile(tokenFile)
	stk := string(tk)
	if stk != "" {
		req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", stk))
	}

	// send request
	resp, err := client.Do(req)
	if err != nil {
		return false, err
	}
	if resp.StatusCode != 200 {
		return false, nil
	}
	return true, nil
}

// send login request
func sendLogin(host string, port int, name string, password string) error {
	endpoint := fmt.Sprintf("http://%s:%d/api/v1/accounts/login", host, port)

	form, _ := json.Marshal(map[string]interface{}{
		"name":     name,
		"password": password,
	})

	resp, err := http.Post(endpoint, "application/json", bytes.NewReader(form))
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	rspData, err := ioutil.ReadAll(resp.Body)
	switch resp.StatusCode {
	case 200:
		// get data
		if err != nil {
			return err
		}
		md := struct {
			Jwt []byte
		}{}
		// parse data
		if err := json.Unmarshal(rspData, &md); err != nil {
			return err
		}
		// write token to file
		return ioutil.WriteFile(tokenFile, md.Jwt, 0644)
	case 400:
		infra.Log.Info("wrong username/password")
		return nil
	}

	infra.LogT.PrintInfo("response data: %s", string(rspData))
	return fmt.Errorf("send request error")
}

func init() {
	tokenFile = os.TempDir() + "/obs-token-cache"

	// query string
	httpGetCmd.Flags().StringSliceP("qs", "q", []string{}, "query string")
	viper.BindPFlag("qs", httpGetCmd.Flags().Lookup("qs"))

	// host
	httpGetCmd.Flags().StringVarP(&host, "host", "h", "127.0.0.1", "request host")
	httpGetCmd.Flags().IntVarP(&port, "port", "p", 12138, "request port")
}
