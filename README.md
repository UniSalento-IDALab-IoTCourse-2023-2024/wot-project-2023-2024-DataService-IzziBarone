# SmartLocAI - DataService API

## Overview

La **SmartLocAI DataService API** è un servizio backend sviluppato con **Flask** che gestisce la raccolta, l'archiviazione e la gestione dei dati RSSI (Received Signal Strength Indicator) utilizzati per la localizzazione indoor. I dati raccolti vengono memorizzati in **MongoDB**, e il servizio fornisce funzionalità per il caricamento, la modifica, la cancellazione e la visualizzazione dei dati. Questo API è anche responsabile del versionamento dei dati raccolti e gestisce informazioni di storicizzazione per garantire la tracciabilità dei punti di riferimento utilizzati per l'addestramento dei modelli di machine learning.

## a) Architettura del Sistema

Il **DataService API** fa parte dell'architettura modulare di **SmartLocAI** ed è uno dei componenti centrali per la gestione e il preprocessing dei dati RSSI utilizzati per addestrare i modelli K-Means e KNN.

### Flusso di lavoro:

1. **Raccolta dei dati**: L'app mobile raccoglie i dati RSSI e li invia al **DataService API**.
2. **Archiviazione**: Il **DataService** verifica i dati ricevuti e li memorizza nel database MongoDB. Se i dati esistono già, vengono aggiornati e aggregati.
3. **Preprocessing**: I dati raccolti possono essere visualizzati, aggiornati o eliminati tramite richieste POST, GET, PUT e DELETE.
4. **Utilizzo per addestramento**: I dati vengono successivamente utilizzati dalla **Preprocessing Dashboard** per addestrare i modelli di machine learning.

## b) Repositories dei Componenti

- **Preprocessing Dashboard**: [Link al repository](https://github.com/UniSalento-IDALab-IoTCourse-2023-2024/wot-project-2023-2024-Dashboard-IzziBarone.git)
- **LocalizationService API**: [Link al repository](https://github.com/UniSalento-IDALab-IoTCourse-2023-2024/wot-project-2023-2024-LocalizationService-IzziBarone)
- **SmartLocAI App**: [Link al repository](https://github.com/UniSalento-IDALab-IoTCourse-2023-2024/wot-project-2023-2024-SmartLocAI_APP-IzziBarone.git)

## c) Endpoint Principali del DataService API

### 1. Gestione dei dati RSSI

- **POST /data**: Aggiunge nuovi dati RSSI o aggiorna i dati esistenti.
   - Esempio di request:
     ```json
     {
       "x": 10,
       "y": 20,
       "data": [{"rssiA": -70, "rssiB": -65}],
       "date": "2024-01-01"
     }
     ```
   - Risposta: `201 Created` se il documento è stato creato, `200 OK` se è stato aggiornato.

- **GET /data**: Restituisce tutti i dati RSSI archiviati.
   - Risposta: `200 OK` con tutti i dati, o `404 Not Found` se non sono presenti dati.

- **DELETE /data**: Elimina un documento specifico in base all'ID.
   - Esempio di request:
     ```json
     {
       "id": "60b9e7b2f1e1463d7b3d492b"
     }
     ```
   - Risposta: `200 OK` se il documento è stato rimosso, `404 Not Found` se non esiste.

- **PUT /data**: Aggiorna un documento specifico in base all'ID.
   - Esempio di request:
     ```json
     {
       "id": "60b9e7b2f1e1463d7b3d492b",
       "x": 15,
       "y": 25,
       "data": [{"rssiA": -68, "rssiB": -60}],
       "date": "2024-01-02"
     }
     ```
   - Risposta: `200 OK` se il documento è stato aggiornato.

### 2. Gestione dei dati di test

- **POST /data/test**: Aggiunge dati di test utilizzati per verificare il modello.
   - Esempio di request:
     ```json
     {
       "RP": "Reference Point 1",
       "data": [{"rssiA": -72, "rssiB": -66}]
     }
     ```
   - Risposta: `201 Created`.

- **GET /data/test**: Restituisce tutti i dati di test.

### 3. Gestione delle coordinate spaziali

- **GET /data/space/coordinates**: Restituisce la cronologia di tutte le coppie di coordinate (x, y).

### 4. Gestione degli SSID

- **POST /data/ssid**: Aggiunge o aggiorna informazioni SSID.
   - Esempio di request:
     ```json
     {
       "ssid": "SSID123",
       "type": "A"
     }
     ```
   - Risposta: `201 Created`.

- **DELETE /data/ssid**: Elimina un SSID specifico.
   - Esempio di request:
     ```json
     {
       "ssid": "SSID123"
     }
     ```
   - Risposta: `200 OK` se l'SSID è stato eliminato.

- **GET /data/ssid**: Restituisce tutti gli SSID memorizzati.

---

### Come Iniziare

1. Clona il repository:
   ```bash
   git clone https://github.com/link-dataservice-api.git
   ```
2. Variabili d'ambiente:
   ```yml
      - DATABASE_URL=mongodb://db:27017/database
      - DATABASE=database
      - JWT_SECRET=******
      - USERNAME=*******
      - PASSWORD=*******
   ```
4. Docker compose
   ```bash
   docker compose up -d
   ```

### Autenticazione

Tutti gli endpoint che gestiscono dati (POST, PUT, DELETE) richiedono l'autenticazione tramite **JWT** (JSON Web Token). Per ottenere un token JWT, è necessario autenticarsi tramite l'[API](https://github.com/UniSalento-IDALab-IoTCourse-2023-2024/wot-project-2023-2024-LocalizationService-IzziBarone) di login, e includere il token nelle intestazioni di tutte le richieste protette.
