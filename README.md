# postobot

## Configurazione
+ Crea un bot su Telegram con [BotFather](https://t.me/botfather)
+ Configura la variabile d'ambiente `BOT_TOKEN` il token che ti ha dato BotFather
+ Configura i comandi del bot con `/mybots -> scegli il tuo bot -> edit bot -> edit commands`:
  ```
  start - Avvia il bot e stampa il messaggio principale
  prenota - Prenota una lezione tra quelle disponibili
  prenotate - Ottieni il QR di una lezione tra quelle prenotate
  cancella - Cancella una lezione tra quelle prenotate
  annulla - Annulla la procedura corrente
  ```
+ \[Opzionale\]: per maggiore sicurezza puoi settare il bot in modo che i comandi siano usabili solo da te, per farlo e' sufficiente settare la variabile di ambiente `CHAT_ID`, puoi ottenerlo contattando [IDBot](http://t.me/myidbot).

## Deployment

### Deploy tradizionale (raccomandato)

Esempio di  `docker-compose.yml`
```yml
version: "3.1"
services:
  db:
    image: postgres:alpine
    restart: always
    ports:
      - 5432:5432
    environment:
      POSTGRES_USER: postgres
      POSTGRES_DB: postobot
      POSTGRES_PASSWORD: <POSTGRES_PASSWORD>

  bot:
    image: registry.gitlab.com/
    environment:
      CHAT_ID: <CHAT_ID>
      BOT_TOKEN: <BOT_TOKEN>
      MATRICOLA: <MATRICOLA>
      PASSWORD: <PASSWORD>
      DATABASE_URL: postgresql+psycopg2://postgres:<POSTGRES_PASSWORD>@db/postobot
```

### Deploy su Heroku

Se hai un account Heroku


[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/rcastellotti/postobot/tree/heroku)
