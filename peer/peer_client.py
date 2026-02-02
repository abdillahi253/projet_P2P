import socket
import json
import os
from protocol import *

CENTRAL_HOST = "192.168.2.61"
CENTRAL_PORT = 9090
SHARED_DIR = "/~/shared"

def search(sock, keyword):
    sock.send(f"{SEARCH} {keyword}".encode(ENCODING))
    data = sock.recv(BUFFER_SIZE).decode(ENCODING)
    return json.loads(data)

def download(owner, port, filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((owner, port))
    s.send(f"{GET} {filename}".encode(ENCODING))

    # S'assurer que le dossier 'shared' existe
    os.makedirs(SHARED_DIR, exist_ok=True)
    path = os.path.join(SHARED_DIR, filename)
    with open(path, "wb") as f:
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

    while True:
        user_input = input("Voulez-vous rechercher un fichier? (o/n): ")
        if user_input.lower() != 'o':
            break
        keyword = input("Mot-clé: ")
        results = search(sock, keyword)

        print("Résultats:")
        if results:
            headers = ["#", "Nom", "Description", "Owner", "Port"]
            row_format = "{:<3} {:<20} {:<30} {:<15} {:<6}"
            print(row_format.format(*headers))
            print("-" * 80)
            for i, r in enumerate(results, 1):
                print(row_format.format(
                    i,
                    r.get('filename', ''),
                    r.get('description', ''),
                    r.get('owner', ''),
                    r.get('port', '')
                ))
        else:
            print("Aucun résultat trouvé.")

        if results:
            choix = input("Numéros des fichiers à télécharger (ex: 1,2,3) : ")
            nums = [int(x.strip()) for x in choix.split(",") if x.strip().isdigit()]
            for n in nums:
                if 1 <= n <= len(results):
                    r = results[n-1]
                    print(f"Téléchargement de {r['filename']} depuis {r['owner']}:{r['port']}...")
                    download(r['owner'], r['port'], r['filename'])
                else:
                    print(f"Numéro {n} invalide.")
        


if __name__ == "__main__":
    main()