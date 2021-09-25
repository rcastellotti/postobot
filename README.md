# postobot
1. bot father -> token
2. avvia il bot e scrivigli `/my_id`
3. andate a questo url `https://api.telegram.org/bot<ILTUOBOTROKEN>/getUpdates`
4. avrete una risposta come questa, prendete result[chat][id]:
```
{
  "ok": true,
  "result": [
    {
      "update_id": 987654321,
      "message": {
        "message_id": 366,
        "from": {
          "id": 123456789,
          "is_bot": false,
          "first_name": "F",
          "username": "Fabifont",
          "language_code": "en"
        },
        "chat": {
          "id": 123456789,
          "first_name": "F",
          "username": "Fabifont",
          "type": "private"
        },
        "date": 1632561784,
        "text": "/my_id",
        "entities": [
          {
            "offset": 0,
            "length": 6,
            "type": "bot_command"
          }
        ]
      }
    }
  ]
}
```

poi ci sono due strade

5. settate le variabili d'ambiente nel .env
6. docker

oppure

5. deploy su heroku
6. settate le variabili d'ambiente su heroku

oppure deploy docker su heroku (meh)

botfather -> /mybots -> scegli il tuo bot -> edit bot -> edit commands e invia:
```
start - Avvia il bot e stampa il messaggio principale
prenota - Prenota una lezione tra quelle disponibili
prenotate - Ottieni il QR di una lezione tra quelle prenotate
cancella - Cancella una lezione tra quelle prenotate
annulla - Annulla la procedura corrente
```
