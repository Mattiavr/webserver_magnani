import socket
import threading
import os
import yaml
import logging


def handle_client(client_socket, address, config):
    """
    Gestisce la comunicazione con un singolo client usando il routing dinamico.
    """

    logging.info(f"[NUOVA CONNESSIONE] {address} collegato.")

    try:
        request_data = client_socket.recv(1024).decode('utf-8')
        if not request_data:
            return

        first_line = request_data.split('\n')[0]
        path_requested = first_line.split(' ')[1]

        file_to_serve = None
        for route in config['routes']:
            if route['path'] == path_requested:
                file_to_serve = route['file']
                break

        if file_to_serve:
            full_path = os.path.join(config['static_dir'], file_to_serve)
            estensione = os.path.splitext(file_to_serve)[1]
            content_type = config['mime_types'].get(estensione, "text/plain")

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                response_body = content
                status = "HTTP/1.1 200 OK"
            except FileNotFoundError:
                response_body = "<h1>404 Not Found</h1><p>File fisico non trovato.</p>"
                status = "HTTP/1.1 404 NOT FOUND"
                content_type = "text/html"
        else:
            response_body = "<h1>404 Not Found</h1><p>Rotta non definita.</p>"
            status = "HTTP/1.1 404 NOT FOUND"
            content_type = "text/html"

        response_headers = (
            f"{status}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(response_body.encode('utf-8'))}\r\n"
            "Connection: close\r\n\r\n"
        )
        client_socket.sendall((response_headers + response_body).encode('utf-8'))

        # Log dell'esito della richiesta
        logging.info(f"Richiesta: {path_requested} -> Risposta: {status}")

    except Exception as e:
        # Sostituito print con logging.error
        logging.error(f"[ERRORE] {e}")
    finally:
        client_socket.close()
        # Sostituito print con logging.info
        logging.info(f"[DISCONNESSIONE] {address} chiuso.")


def load_config():
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
    config = load_config()
    if config is None:
        print("Server interrotto per mancanza di configurazione")
        return

    # --- CONFIGURAZIONE LOGGING ---
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