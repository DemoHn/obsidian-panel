**author: Nigshoxiz**
**date: 19/10/2016**

## Message Queue Protocol

0. Definitions
- module : Obsidian Panel is separated of several **independent and parallel** modules. Each module is a separate process,
monitored by `circus`, a process monitor.
- MPW : `Minecraft Process Watcher` module
- WS  : `Websocket Server` module
- APP : `Main app` module
- FTM : `FTP Manager` module

1. Introduction
Due to the modules (e.g. MPW, WS, APP, FTM) are running in separate processes,
It's impossible to access those modules directly.

In order to communicate with each other, a messaging protocol is
developed based on [Message Queue](https://www.wikiwand.com/en/Message_queue).

Why message queue? Though this question is not related to this topic, but I'm willing
to answer it: Because of WebSocket. I have realized that if we just integrate the WebSocket module
into the app (just like many servers do), it will take a bunch of serious problem, like
we can't fork add process, and the latent GIL issues. Thus I separated it and make the
WebSocket server standalone. This take the issues of communicating with main App process and
WebSocket server process, and then I introduced message queue.

There're many implementations of message queue. I choose **Redis** for this project.

Also, I choose PUB/SUB as message queue model. That is, when a module (_Publisher_) send a message,
all other modules (_Subscriber_) will receive this message.

2. Message Format

Here is the message for notification
```
{
    "event" : <event name>,
    "to" : <module TAG>,
    "props": <values>,
    "flag" : <flag>,
    "_uid" : <uid>,
    "_sid" : <sid> or None
}
```

