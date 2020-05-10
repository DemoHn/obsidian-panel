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

### proc auto-restart background thread

will constantly check if a process has been exited (per **15** seconds)