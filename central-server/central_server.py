import socket
import threading
import json
from protocol import *

HOST = "192.168.2.61"
PORT = 9090

index = [] # fichiers partagés
active_peers = {} # username -> (host, port)


def handle_client(conn, addr):
    print("Connexion de", addr)
    while True:
        data = conn.recv(BUFFER_SIZE).decode(ENCODING)
        if not data:
            print("Client déconnecté:", addr)
            break

        parts = data.split(" ", 1)
        cmd = parts[0]

        if cmd == LOGIN:
            parts2 = parts[1].split(" ", 1)
            username, pwd_hash = parts2[0], parts2[1]
            if users.get(username) == pwd_hash:
                conn.send(OK.encode(ENCODING))
            elif username not in users:
                users[username] = pwd_hash
                save_users()
                conn.send(OK.encode(ENCODING))
            else:
                conn.send(FAIL.encode(ENCODING))

        elif cmd == LOAD:
            payload = parts[1]
            data = json.loads(payload)
            if data.get('owner') not in index:
                index.append(data)
                save_index()
            elif data.get('owner') in index:
                existing = next(f for f in index if f['owner'] == data['owner'])
                existing['files'] = data['files']
                save_index()
            conn.send(OK.encode(ENCODING))
            
        elif cmd == SEARCH:
            keyword = parts[1].lower()
            results = []
            for entry in index:
                # Exclure les fichiers dont le propriétaire est l'utilisateur lui-même
                if entry.get('owner') == addr[0]:
                    continue
                for f in entry['files']:
                    if keyword in f['description'].lower():
                        # Ajoute owner et port à chaque résultat
                        result = f.copy()
                        result['owner'] = entry.get('owner')
                        result['port'] = entry.get('port')
                        results.append(result)
            conn.send(json.dumps(results).encode(ENCODING))


    conn.close()

def save_users():
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f)

def load_users():
    global users
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}

def save_index():
    with open("index.json", "w", encoding="utf-8") as f:
        json.dump(index, f)

def load_index():
    global index
    try:
        with open("index.json", "r", encoding="utf-8") as f:
            index = json.load(f)
    except FileNotFoundError:
        index = []

def main():
    load_users()
    load_index()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    print("Serveur central en écoute sur", PORT)


    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()




if __name__ == "__main__":
    main()