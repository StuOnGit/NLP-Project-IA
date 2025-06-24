# NLP-Project-IA


# IFTTT doc.
1. Oggetti chiave

    Meta → oggetto che fornisce dati sul tempo e l'utente

    Trigger → contiene le informazioni sull’evento che ha scatenato la regola

    Action → oggetto che rappresenta l’azione da eseguire (con proprietà)

    IfNotifications, Email, Telegram, GoogleSheets, Domovea, ecc. → servizi/actions

2. Metodi comuni

    skip() → per saltare un’azione

    sendNotification(), runScene(), addRowToSheet() → funzioni delle action

3. Proprietà comuni

    Meta.currentUserTime, Trigger.subject, Trigger.body, ecc