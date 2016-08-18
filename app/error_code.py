__author__ = 'Nigshoxiz'
# date : 2015-11-17
# errcode

errcode = {}

errcode['300'] = "outdated"

# refuse op
errcode['340'] = "refuse operation"

errcode['400'] = "json parsing error"
errcode['401'] = "input data is not complete"
errcode['403'] = "Operation Forbidden"

errcode['405'] = "invalid keyword"
# file upload
errcode['411'] = "file extension not allowed"

# new_service dispatch error
errcode['420'] = "dispatch unknown error"
errcode['421'] = "dispatch out of quota"
errcode['422'] = "can't dispatch a port"
errcode['423'] = "create instance error"
errcode['424'] = "process creation error"

# service_idf error
errcode['430'] = "service_idf not available"
errcode['431'] = "device num is full"
errcode['432'] = "identifier collision!!"
# process error
errcode['450'] = "kill process error"
errcode["451"] = "create process error"

# when triggering try...except...
errcode["500"] = "fatal error"
errcode['520'] = "data is null"

# database
errcode["600"] = "database error"
errcode["610"] = "can't fetch data"
errcode["620"] = "data is null"
errcode["621"] = "ssid does not exist"
errcode["631"] = "service name not unique"
errcode["700"] = "illegal command"

# server_list change_remains error
errcode["710"] = "decline too much"
errcode["720"] = "lid not active"
errcode["730"] = "quota setting error"
errcode["740"] = "register server error"
# login
errcode["730"] = "username duplicated"
errcode["731"] = "no such account"

#register error
errcode["800"] = "null username is illegal"
errcode["801"] = "password should not shorter than six characters"

errcode["810"] = "unknown error"
errcode["811"] = "no such username"
errcode["812"] = "password error"

errcode["830"] = "auth error"

# check purchase string
errcode["840"] = "purchase check error"
errcode["841"] = "no service to purchase"

# register new sub-server
errcode["860"] = "server key error"

errcode["880"] = "HTTP communication error"
errcode["881"] = "socket timeout"
errcode["882"] = "HTTP execute error"
# bind error
errcode["900"] = "bind account error"
errcode["901"] = "router IDF not unique"

# wallet
errcode["1000"] = "balance not enough"
errcode["1001"] = "recharge amount is larger than upper limit"
# pricing strategy
errcode["1010"] = "strategy name error"

#dispatch
errcode["1020"] = "no server to dispatch"
errcode["1021"] = "dispatch fails"
#etc
errcode["1120"] = "quota adjust error"

# free service
errcode["1200"] = "already accepted a free service"