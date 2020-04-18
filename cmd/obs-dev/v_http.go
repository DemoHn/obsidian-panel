package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"strconv"
	"strings"

	"github.com/AlecAivazis/survey/v2"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

var (
	tokenFile string
	gHost     string
	gPort     int

	promptName = &survey.Input{
		Message: "Login as:",
	}

	promptPassword = &survey.Password{
		Message: "Password:",
	}
)

// Example Command:
// obs-dev http:get /api/v1/accounts -h 127.0.0.1 -p 12138 --qs hello=1,world=2
var httpGetCmd = &cobra.Command{
	Use:   "http:get",
	Short: "Send HTTP GET request to panel; usually for testing",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		var name string
		var password string
		qs, _ := viper.Get("qs").([]string)
		// I. do get
		res, err := doGet(gHost, gPort, args[0], qs)
		if err != nil {
			return err
		}
		if !res {
			survey.AskOne(promptName, &name)
			survey.AskOne(promptPassword, &password)
			if err := sendLogin(gHost, gPort, name, password); err != nil {
				return err
			}

			// II. do get again
			_, err := doGet(gHost, gPort, args[0], qs)
			if err != nil {
				return err
			}
		}
		return nil
	},
}

var httpPostCmd = &cobra.Command{
	Use:   "http:post",
	Short: "Send HTTP POST request to panel; usually for testing",
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		var name string
		var password string

		dv, _ := viper.Get("data").([]string)
		ds, _ := viper.Get("data-str").([]string)
		data := parseToJSONStr(dv, ds)

		// I. do post
		res, err := doPost(gHost, gPort, args[0], data)
		if err != nil {
			return err
		}
		if !res {
			survey.AskOne(promptName, &name)
			survey.AskOne(promptPassword, &password)
			if err := sendLogin(gHost, gPort, name, password); err != nil {
				return err
			}

			// II. do post again
			_, err := doPost(gHost, gPort, args[0], data)
			if err != nil {
				return err
			}
		}
		return nil
	},
}

func doGet(host string, port int, url string, qs []string) (bool, error) {
	qss := strings.Join(qs, "&")
	endpoint := fmt.Sprintf("http://%s:%d%s?%s", host, port, url, qss)

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
	data, _ := ioutil.ReadAll(resp.Body)
	if resp.StatusCode != 200 {
		if resp.StatusCode == 401 {
			infra.LogT.PrintInfo("Not Authorized! will ask for login")
		} else {
			infra.LogT.PrintInfo("response data: %s", string(data))
			return false, fmt.Errorf("response data")
		}
		return false, nil
	}
	infra.LogT.PrintInfo("response data: %s", string(data))
	return true, nil
}

// send POST request
func doPost(host string, port int, url string, dataBuf string) (bool, error) {
	endpoint := fmt.Sprintf("http://%s:%d%s", host, port, url)

	client := new(http.Client)
	req, _ := http.NewRequest("POST", endpoint, bytes.NewReader([]byte(dataBuf)))
	req.Header.Set("Content-Type", "application/json")
	// read data
	tk, _ := ioutil.ReadFile(tokenFile)
	stk := string(tk)
	if stk != "" {
		req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", stk))
	}

	resp, err := client.Do(req)
	if err != nil {
		return false, err
	}
	data, _ := ioutil.ReadAll(resp.Body)
	if resp.StatusCode != 200 {
		if resp.StatusCode == 401 {
			infra.LogT.PrintInfo("Not Authorized! will ask for login")
		} else {
			infra.LogT.PrintInfo("response data: %s", string(data))
			return false, fmt.Errorf("response error")
		}
		return false, nil
	}
	infra.LogT.PrintInfo("response data: %s", string(data))
	return true, nil
}

// parse <key>=<value> slice to json string
// dv => <key>=<value>, value will be int if all chars are digits
// ds => <key>=<value>, value will be string type
func parseToJSONStr(dv []string, ds []string) string {
	var final = map[string]interface{}{}
	// parse dv
	for _, itemv := range dv {
		var key = itemv

		arr := strings.Split(itemv, "=")
		if len(arr) > 1 {
			key = arr[0]
			final[key] = arr[1]
			if digits, err := strconv.Atoi(arr[1]); err == nil {
				final[key] = digits
			}

		} else {
			final[key] = itemv
		}
	}
	// parse ds
	for _, items := range ds {
		var key = items

		arr := strings.Split(items, "=")
		if len(arr) > 1 {
			key = arr[0]
			final[key] = arr[1]
		} else {
			final[key] = items
		}
	}

	bytes, _ := json.Marshal(final)
	return string(bytes)
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
			Jwt string
		}{}
		// parse data
		if err := json.Unmarshal(rspData, &md); err != nil {
			return err
		}
		// write token to file
		return ioutil.WriteFile(tokenFile, []byte(md.Jwt), 0644)
	case 400:
		infra.LogT.PrintInfo(string(rspData))
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

	httpPostCmd.Flags().StringSliceP("data", "d", []string{}, "data item, <key>=<value> format")
	viper.BindPFlag("data", httpPostCmd.Flags().Lookup("data"))

	httpPostCmd.Flags().StringSliceP("data-str", "s", []string{}, "data item, <key>=<value> format, must be string")
	viper.BindPFlag("data-str", httpPostCmd.Flags().Lookup("data-str"))

	// host, port
	httpGetCmd.Flags().StringVarP(&gHost, "host", "H", "127.0.0.1", "request host")
	httpGetCmd.Flags().IntVarP(&gPort, "port", "p", 12138, "request port")

	// host
	httpPostCmd.Flags().StringVarP(&gHost, "host", "H", "127.0.0.1", "request host")
	httpPostCmd.Flags().IntVarP(&gPort, "port", "p", 12138, "request port")
}
