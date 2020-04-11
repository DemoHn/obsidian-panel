# obsidian-panel

TODO

## Requires

- protoc

## Build & Install

- `obs` command:
```sh
cd obsidian-panel
go build -o obs
```

- `obs-dev` command:
```sh
go build cmd/obs-dev -o obs-dev
```

## Installation (OLD)

- Install `task` as an alternative of `Makefile`:
```sh
go get -u -v github.com/go-task/task/cmd/task
```

- Test Project
```sh
task test
```

- Build Project
```sh
task build
```
