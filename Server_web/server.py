import socket
import threading
import os
import yaml
import logging


def handle_client(client_socket, address, config):
    """
    Gestisce la comunicazione con un singolo client usando il routing dinamico.
    Questa funzione viene eseguita in un thread separato per ogni connessione.
    """

    logging.info(f"[NUOVA CONNESSIONE] {address} collegato.")

    try:
       
        # Riceve la richiesta HTTP dal browser (max 1024 byte)
        request_data = client_socket.recv(1024).decode('utf-8')
        if not request_data:
            return

        
        # Estraiamo il percorso
        # Dividiamo la stringa per righe e poi prendiamo il secondo elemento della prima riga
        first_line = request_data.split('\n')[0]
        path_requested = first_line.split(' ')[1]

       
        # Cerchiamo se il path richiesto dal browser esiste nella sezione 'routes' del YAML
        file_to_serve = None
        for route in config['routes']:
            if route['path'] == path_requested:
                file_to_serve = route['file']
                break

        
        if file_to_serve:
            # Costruisce il percorso completo unendo la cartella statica e il nome file
            full_path = os.path.join(config['static_dir'], file_to_serve)
            
            # Determina l'estensione per impostare il Content-Type corretto (es: .html, .css)
            estensione = os.path.splitext(file_to_serve)[1]
            content_type = config['mime_types'].get(estensione, "text/plain")

            try:
                # Tenta di leggere il contenuto del file fisico
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                response_body = content
                status = "HTTP/1.1 200 OK"
            except FileNotFoundError:
                # Caso in cui la rotta esiste nel YAML ma il file manca nella cartella
                response_body = "<h1>404 Not Found</h1><p>File fisico non trovato.</p>"
                status = "HTTP/1.1 404 NOT FOUND"
                content_type = "text/html"
        else:
            # Caso in cui l'utente chiede un URL non previsto nel file YAML
            response_body = "<h1>404 Not Found</h1><p>Rotta non definita.</p>"
            status = "HTTP/1.1 404 NOT FOUND"
            content_type = "text/html"

        
        # Assembla gli header secondo lo standard HTTP/1.1
        response_headers = (
            f"{status}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(response_body.encode('utf-8'))}\r\n"
            "Connection: close\r\n\r\n"
        )
        # Invia tutto al client convertendo la stringa in byte
        client_socket.sendall((response_headers + response_body).encode('utf-8'))

        # Log dell'esito della richiesta nel file server.log
        logging.info(f"Richiesta: {path_requested} -> Risposta: {status}")

    except Exception as e:
        # Gestione errori generici per evitare il crash del thread
        logging.error(f"[ERRORE] {e}")
    finally:
        # CHIUSURA CONNESSIONE
        client_socket.close()
        logging.info(f"[DISCONNESSIONE] {address} chiuso.")


def load_config():
    """
    Carica la configurazione del server dal file esterno YAML.
    """
    try:
        with open('server_config.yaml', 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        print("File di configurazione non trovato")
        return None
    except yaml.YAMLError as exc:
        print(f"Errore sintassi YAML: {exc}")
        return None


def start_server():
    """
    Inizializza il server, configura il logging e gestisce il ciclo di accettazione client.
    """
    config = load_config()
    if config is None:
        print("Server interrotto per mancanza di configurazione")
        return

    # CONFIGURAZIONE LOGGING
    # Imposta il file di destinazione e il livello presi dal YAML
    logging.basicConfig(
        filename=config['logging']['file'],
        level=config['logging']['level'],
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = config['server']['host']
    port = config['server']['port']
    server.bind((host, port))
    server.listen(config["server"]["max_connections"])

    # Messaggio di avvio sia su console che su log
    msg_start = f"[START] Server in ascolto su http://{host}:{port}"
    print(msg_start)
    logging.info(msg_start)

    while True:
        client_sock, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_sock, addr, config))
        thread.start()

        # Log dei thread attivi
        logging.info(f"[THREAD ATTIVI] {threading.active_count() - 1}")


if __name__ == "__main__":

    start_server()
