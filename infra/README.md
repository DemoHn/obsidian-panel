# Folder `infra/`

Defines the infrastructure of `obsidian-panel` project that every provider, driver relies on.

It will **MUST** be initialized at the beginning and as the very first dependency to be injected to other
providers, drivers, and so on. The difference between `infra` and `drivers` is clear: `drviers` are optional, while `infra` isn't.