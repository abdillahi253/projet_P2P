import socket
import threading
import os
import json
from protocol import *
from cryptpwd import hash_password

HOST = "192.168.2.144"
PORT = 9000
SHARED_DIR = "~/shared"
CENTRAL_HOST = "192.168.2.61"
CENTRAL_PORT = 9090

def login(username, password):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((CENTRAL_HOST, CENTRAL_PORT))
    msg = f"{LOGIN} {username} {hash_password(password)}"
    s.send(msg.encode(ENCODING))
    resp = s.recv(BUFFER_SIZE).decode(ENCODING)
    return resp == OK, s

def logout(sock):
    msg = LOGOUT
    sock.send(msg.encode(ENCODING))
    resp = sock.recv(BUFFER_SIZE).decode(ENCODING)
    return resp == OK

def load_descriptions(sock):
        
    with open("shared/description.JSON", "r", encoding="utf-8") as f:
        descriptions = json.load(f)

    desc = {"owner": HOST, "port": PORT, "files": descriptions}
    payload = json.dumps(desc)
    data = f"{LOAD} {payload}"
    sock.send(data.encode(ENCODING))
    resp = sock.recv(BUFFER_SIZE).decode(ENCODING)
    return resp == OK, sock

def handle_client(conn, addr):
    request = conn.recv(BUFFER_SIZE).decode(ENCODING)
    cmd, filename = request.split()

    if cmd == GET:
        if addr[0] != HOST:
            path = os.path.join(SHARED_DIR, filename)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    while chunk := f.read(BUFFER_SIZE):
                        conn.send(chunk)
    conn.close()

def listen():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    print("Serveur P2P actif sur", PORT)

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()



def main():
    username = input("Nom d'utilisateur: ")
    pwd = input("Mot de passe: ")

    ok, s1 = login(username, pwd)
    if not ok:
        print("Authentification échouée")

        return

    ok, s1 = load_descriptions(s1)
    if not ok:
        print("Échec du chargement des descriptions")
        return

    # Lancer le serveur P2P
    listen()


if __name__ == "__main__":
    main()