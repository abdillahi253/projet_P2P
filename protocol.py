# protocol.py


ENCODING = "utf-8"
BUFFER_SIZE = 4096


# Commandes client → serveur central
LOGIN = "LOGIN"
REGISTER = "REGISTER"
SEARCH = "SEARCH"
UPDATE = "UPDATE"
LOGOUT = "LOGOUT"
LOAD = "LOAD"


# Réponses serveur
OK = "OK"
FAIL = "FAIL"


# P2P
GET = "GET"