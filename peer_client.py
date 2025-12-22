import socket
import json
from protocol import *

CENTRAL_HOST = "192.168.2.61"
CENTRAL_PORT = 9090

def search(sock, keyword):
    sock.send(f"{SEARCH} {keyword}".encode(ENCODING))
    data = sock.recv(BUFFER_SIZE).decode(ENCODING)
    return json.loads(data)

def download(owner, port, filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((owner, port))
    s.send(f"{GET} {filename}".encode(ENCODING))

    with open(filename, "wb") as f:
        while data := s.recv(BUFFER_SIZE):
            f.write(data)
    s.close()

def connect_to_central_server():
    print(f"Connexion au serveur central ({CENTRAL_HOST}:{CENTRAL_PORT})...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((CENTRAL_HOST, CENTRAL_PORT))
    return sock

def main():
    sock = connect_to_central_server()
    if not sock:
        return

    keyword = input("Mot-clé: ")
    results = search(sock, keyword)

    print("Résultats:")
    for r in results:
        print(r)

    if results:
        r = results[0]
        download(r['owner'], r['port'], r['filename'])


if __name__ == "__main__":
    main()