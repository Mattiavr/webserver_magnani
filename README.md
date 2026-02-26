# webserver_magnani
repository per la consegna webserver

# Simple Multithreaded Web Server in Python
Caratteristiche principali
**Gestione Multi-thread**: Ogni connessione client viene gestita in un thread separato per garantire la non-interattività e supportare richieste simultanee.
* **Routing Dinamico**: Le rotte (URL) e i file associati sono configurabili esternamente tramite YAML.
* **MIME-Type Handling**: Supporto a diversi tipi di file (HTML, CSS, ecc.) con intestazioni `Content-Type` generate dinamicamente.
* **Logging Avanzato**: Sistema di tracciamento su file e console per monitorare accessi ed errori in tempo reale.
* **Sicurezza**: Accesso limitato alla sola cartella specificata come `static_dir`.


Scelte Implementative

1. Concorrenza con il modulo `threading`
Per evitare che il server si blocchi durante la gestione di una singola richiesta, è stato utilizzato il modulo `threading`. Il thread principale rimane costantemente in ascolto (`accept()`), mentre per ogni client viene creato un worker thread dedicato alla funzione `handle_client`.

2. Configurazione centralizzata (YAML)
È stato scelto il formato YAML per la sua leggibilità. Il file `server_config.yaml` permette di modificare parametri critici (porta, host, numero massimo di connessioni) senza dover toccare il codice sorgente Python.

3. Logica di Routing e MIME-Types
Il server non si limita a servire un file statico fisso. Analizza la prima riga della richiesta HTTP per estrarre il percorso richiesto:
Confronta il percorso con la sezione `routes` dello YAML.
Determina l'estensione del file tramite `os.path.splitext`.
Assegna il corretto header `Content-Type` mappando l'estensione nel dizionario `mime_types`.

4. Sistema di Logging
Invece di semplici `print`, è stata implementata la libreria `logging` di sistema. Questo permette di:
Salvare lo storico delle operazioni nel file `server.log`.
Filtrare i messaggi per gravità (INFO, ERROR, DEBUG).
Mantenere traccia dei timestamp per ogni operazione.

