

# cmdspliter
`import "."`

* [Overview](#pkg-overview)
* [Index](#pkg-index)

## <a name="pkg-overview">Overview</a>
Package cmdspliter intends to immitate bash way to split a string command to
an array of arguments

For example:
"/bin/cmd -f 'a.zip b.zip' -g" => ["/bin/cmd", "-f", "'a.zip b.zip'", "-g"]




## <a name="pkg-index">Index</a>
* [Constants](#pkg-constants)
* [func SplitCommand(command string) (program string, args []string, err error)](#SplitCommand)


#### <a name="pkg-files">Package files</a>
[cmdspliter.go](/src/target/cmdspliter.go) 


## <a name="pkg-constants">Constants</a>
``` go
const (
    TK_NUL  uint8 = 0 // null char (ignored)
    TK_TX   uint8 = 1 // transcode char
    TK_CHAR uint8 = 2 // normal char
    TK_SPX  uint8 = 3 // space (separator)
    TK_SQ   uint8 = 4 // single quote
    TK_DQ   uint8 = 5 // double quote
)
```



## <a name="SplitCommand">func</a> [SplitCommand](/src/target/cmdspliter.go?s=535:611#L20)
``` go
func SplitCommand(command string) (program string, args []string, err error)
```
SplitCommand - separate a string command to progarm and args








- - -
Generated by [godoc2md](http://godoc.org/github.com/davecheney/godoc2md)