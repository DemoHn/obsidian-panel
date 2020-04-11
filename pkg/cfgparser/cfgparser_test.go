package cfgparser

import (
	"os"
	"testing"

	// goblin
	. "github.com/franela/goblin"
)

func Test_Config(t *testing.T) {
	g := Goblin(t)

	g.Describe("ParseMode = yaml", func() {
		var config *Config

		g.BeforeEach(func() {
			config = New("yaml")
			tmpFile, _ := os.OpenFile("tmp.file", os.O_RDWR|os.O_CREATE, 0755)
			tmpFile.WriteString("a: b")
			tmpFile.Close()
		})

		g.AfterEach(func() {
			if _, err := os.Stat("tmp.file"); err == nil {
				os.Remove("tmp.file")
			}
		})

		g.It("Parse YAML correctly /load from data", func() {
			var data = `
str: Easy!
123: F
arr:
  - str_01
  - 2345
  - 34.56780000
dict:
  key01:
    key02: value
  keyA: keyB
  arr:
    - 100
    - dict2:
        map: map2`
			err := config.LoadFromData([]byte(data))

			g.Assert(err).Equal(nil)
			v1, _ := config.Find("str")
			g.Assert(v1).Equal("Easy!")

			v2, _ := config.Find("123")
			g.Assert(v2).Equal("F")

			v3, _ := config.Find("arr.0")
			g.Assert(v3).Equal("str_01")

			v4, _ := config.Find("arr.1")
			g.Assert(v4).Equal(2345)

			v5, _ := config.Find("arr.2")
			g.Assert(v5).Equal(34.5678)

			v6, _ := config.Find("dict.key01.key02")
			g.Assert(v6).Equal("value")

			v7, _ := config.Find("dict.arr.0")
			g.Assert(v7).Equal(100)

			v8, _ := config.Find("dict.arr.1.dict2.map")
			g.Assert(v8).Equal("map2")
		})

		g.It("should load & parse successfully from file", func() {
			err := config.Load("tmp.file")
			g.Assert(err).Equal(nil)

			b, _ := config.Find("a")
			g.Assert(b).Equal("b")
		})

		g.It("should replace Macro", func() {
			var data = `
a: b
c: d`

			parserFunc := func(key string, value interface{}) interface{} {
				if key == "a" {
					return "ccc"
				}
				return value
			}
			config.SetMacroParser(parserFunc)
			config.LoadFromData([]byte(data))

			v1, _ := config.Find("a")
			g.Assert(v1).Equal("ccc")

			v2, _ := config.Find("c")
			g.Assert(v2).Equal("d")
		})

		g.It("should replace dep macro", func() {
			var data = `
apm: apmName
bpm: bpm
merchant.rootDir: /var/www/$(apm)/$(bpm)
merchant.lockFile: $(apm)/exp.lock`

			parserFunc := func(key string, value interface{}) interface{} {
				if key == "apm" {
					return "apmapm"
				}
				return value
			}
			config.SetMacroParser(parserFunc)
			config.LoadFromData([]byte(data))

			v1, _ := config.Find("apm")
			g.Assert(v1).Equal("apmapm")

			v2, _ := config.Find("merchant.rootDir")
			g.Assert(v2).Equal("/var/www/apmapm/bpm")

			v3, _ := config.Find("merchant.lockFile")
			g.Assert(v3).Equal("apmapm/exp.lock")
		})
	})
}
