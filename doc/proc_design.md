## Design doc of `obs-panel` main process manager

### main process

```
+----------------+     spawns    +--------------+
| ./obs -s start |  -----------> |  obs-daemon  |   --> proc1, proc2, ...
+----------------+               +--------------+
```

`obs-daemon` is the core process spawned at background (by `obs -s start`) to handle process management tasks.

after up and running, `obs FG` could interact with `obs-daemon` via unixSocket (default sock path: ~/.obs-root/proc/obs-daemon.sock)

NOTICE: to keep the daemon steady and simple, `obs-daemon` will NEVER read/write DB! All configurations (instance settings) are synced from `obs FG` via unixSocket!

### global variables

- `$rootPath`

`$rootPath` is a global variable injected when `obs-daemon` spawned from `obs FG`. The value would NEVER be null, or the daemon won't start at all!

- `$procSign`

`$procSign` only available inside one instance.

those variables could be used directly on `command`, `stdoutLogFile`, `stderrLogFile`, `directory` example:

```
stdoutLogFile=$rootPath/$procSign/access.log
```

### start process flow

1. `obs FG` spawns `obs-daemon`
2. sync instance configs with `obs-daemon` (via rpc)
3. list all instances that `autoStart = true` and start one by one
4. for each instance:
  - access instance directory (where stores info like pid, restart_times as file) default: `$rootPath/$procSign`
  - check if pid exists (default: `$rootPath/$procSign/pid`)
    - if pid exists, **DONE** with nothing more execution
    - if pid not exists (pid file missing/no active process), try to start instance:
      - after **3 seconds** (which will be configurable in the future), if process not running (pid is active), write counter to a file (default: `$rootPath/$procSign/retry`) and retry again (if retry < `maxRetry`)
      - after **3 seconds**, if process is up and running, **DONE**


### proc folder overview

```
$rootPath (:= ~/.obs-root/proc)
  |
  |-- proc-sign-01/
      |-- pid
      |-- retry
      |-- timestamp
      |-- stop
  |-- proc-sign-02/
      |-- pid
      |-- retry
      |-- timestamp
      |-- stop
  ...

  |-- obs-daemon.pid
  |-- obs-daemon.sock
  |-- obs-daemon.log (OPTIONAL)
  |-- proc-sign-01.log (OPTIONAL)
  |-- proc-sign-02.log (OPTIONAL)
  ...

```

### proc status overview

```
0 - init    (proc)
1 - starting (proc is starting, but not long enough to get the running threshold time (usually 3s))
2 - running  (proc is running constantly)
3 - stopped  (proc stopped manually, so it wouldn't restart)
4 - terminated (proc stopped unexpectedly, will restart shortly if required)
```

NOTE: when a process die before 3s, the status will be "terminated" then!

proc file map table:

|   | init | starting | running | stopped | terminated |
|-----|:----:|:----:|:----:|:----:|:----:|
|pid       | - | - | X | - | - |
|retry     | - | - | - | - | X |
|timestamp | - | X | X | - | - |
|stop      | - | - | - | X | - |

### proc auto-restart background thread (TODO)

will constantly check if a process has been exited (per **15** seconds)

### API design

1. Add instance config

url: `POST /proc/add-instance`

request params:

| param | required | example | description |
| ----- | -------- | ---- | ---- |
| procSign | true | sys-api-server | the only identifier for one instance. must be *unique* |
| name | true | API server | a readable name of the instance |
| command | true | `./obs sys:proc api-server` | execution command  |
| directory | false | `/home/user/xxx` | command execution working directory (if null, it's the directory under which `./obs` is exeucted) |
| env | false | {a: 1, b: 2} | additional env settings |
| autoRestart | false | true | will auto restart if terminated accidentially `(default: true)` |
| stdoutLogFile | false | `/data/log/proc/proc1-access.log` | where to log stdout data `(default: $rootPath/$procSign.log)`|
| stderrLogFile | false | `/data/log/proc/proc1-error.log` | where to log stderr data `(default: $rootPath/$procSign.log)`|
| maxRetry | false | 1 | max time to retry, valid only when _autoRestart=true_ `(0 for unlimited)`|

response data:

```json
{
  "instance": {
    "procSign": "<proc-sign>",
    "name": <name>,
    "command": "...cmd",
    "directory": "/home/data/obs",      
    "env": {},
    "autoRestart": true,
    "maxRetry": 10,
    "stdoutLogFile": "<concrete stdout logFile>",
    "stderrLogFile": "<concrete stderr logFile>",
    "createdAt": <ts>,
    "updatedAt": <ts>
  }
}
```

2. List all instances

url: `GET /proc/list-instances`

request params:

| param | required | example | description |
|----|----|----|----|
| page | false | 1 | `(default: 1)`|
| count | false | 20 | `(default: 20)`|

response data:

```json
{
  "page": 1,
  "count": 20,
  "totalCount": 40,
  "list": [
    {
      "procSign": "<proc-sign>",
      "name": <name>,
      "command": "...cmd",
      "directory": "/home/data/obs",      
      "env": {},
      "autoRestart": true,
      "maxRetry": 10,
      "stdoutLogFile": "<concrete stdout logFile>",
      "stderrLogFile": "<concrete stderr logFile>",
      "createdAt": <ts>,
      "updatedAt": <ts>
    },
    ...
  ]
}
```

3. Edit Instance

url: `POST /proc/edit-instance/:procSign`

request params:

| param | required | example | description |
| ----- | -------- | ---- | ---- |
| procSign | true | sys-api-server | the only identifier for one instance. must be *unique* |
| name | false | API server | a readable name of the instance |
| command | false | `./obs sys:proc api-server` | execution command  |
| directory | false | `/home/user/xxx` | command execution working directory (if null, it's the directory under which `./obs` is exeucted) |
| env | false | {a: 1, b: 2} | additional env settings |
| autoRestart | false | true | will auto restart if terminated accidentially `(default: true)` |
| stdoutLogFile | false | `/data/log/proc/proc1-access.log` | where to log stdout data `(default: $rootPath/$procSign.log)`|
| stderrLogFile | false | `/data/log/proc/proc1-error.log` | where to log stderr data `(default: $rootPath/$procSign.log)`|
| maxRetry | false | 1 | max time to retry, valid only when _autoRestart=true_ `(0 for unlimited)`|

response data:

```json
{
  "instance": {
    "procSign": "<proc-sign>",
    "name": <name>,
    "command": "...cmd",
    "directory": "/home/data/obs",      
    "env": {},
    "autoRestart": true,
    "maxRetry": 10,
    "stdoutLogFile": "<concrete stdout logFile>",
    "stderrLogFile": "<concrete stderr logFile>",
    "createdAt": <ts>,
    "updatedAt": <ts>
  }
}
```

4. Get One Instance

url: `GET /proc/get-instance/:procSign`

request params:

response data:

```json
{
  "instance": {
    "procSign": "<proc-sign>",
    "name": <name>,
    "command": "...cmd",
    "directory": "/home/data/obs",      
    "env": {},
    "autoRestart": true,
    "maxRetry": 10,
    "stdoutLogFile": "<concrete stdout logFile>",
    "stderrLogFile": "<concrete stderr logFile>",
    "createdAt": <ts>,
    "updatedAt": <ts>
  }
}
```

5. Control Instance

url: `POST /proc/control-instance/:procSign`

request params:

| param | required | example | description |
| ----- | -------- | ---- | ---- |
| procSign | true | sys-api-server | the unique process sign |
| op | true | `start`| valid values: `start, stop, restart` |

response data:

```json
{
  "op": <start | stop | restart>,
  "success": true,
  "data": 0,  // for `stop`, it's exitCode
  "failReason": "..."
}
```

6. Stat Instance

url: `GET /proc/stat-instance/:procSign`

response data:

```json
{
  "procSign": <procSign>,
  "stat": {
    "status": <init | starting | running | stopped | terminated>,
    "pid": <number, =0 when not running>,
    "cpu": "0.12345634",        
    "memory": 12343425, // <in bytes>
    "elapsed": 1234 // <in secs>
  }
}
```