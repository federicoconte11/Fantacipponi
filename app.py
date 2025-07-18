from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersegretachiave'  # Cambia questa chiave per sicurezza

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password123'  # Cambiala in una più sicura
settimana_corrente = 1


# Lista amici con logo
amici = [
    {"nome": "Spina", "logo_url": "/static/Alessandro.jpg", "punti": 0},
    {"nome": "Federico", "logo_url": "/static/loghi/federico.jpg", "punti": 0},
    {"nome": "Giamburrasca", "logo_url": "/static/loghi/giamburrasca.png", "punti": 0},
    {"nome": "Aurelio", "logo_url": "/static/loghi/aurelio_carrozzo.png", "punti": 0},
    {"nome": "Carrozzo", "logo_url": "/static/loghi/francesco_carrozzo.png", "punti": 0},
    {"nome": "Denuzzo", "logo_url": "/static/loghi/francesco_denuzzo.png", "punti": 0},
    {"nome": "Birill0", "logo_url": "/static/loghi/birillo.jpg", "punti": 0},
    {"nome": "Domenico", "logo_url": "/static/loghi/domenico_mazza.png", "punti": 0}
]

# Azioni con punti e emoji
azioni_possibili = [
    {"nome": "Serata giocata", "punti": 1, "emoji": "🎉"},
    {"nome": "Serata non giocata", "punti": 0, "emoji": "😴"},
    {"nome": "Sboccata", "punti": -1, "emoji": "🤮"},
    {"nome": "Chi guida", "punti": 1, "emoji": "🚗"},
    {"nome": "Scopata", "punti": 3, "emoji": "🍑"},
    {"nome": "Pompino", "punti": 2, "emoji": "👄"},
    {"nome": "Larciata", "punti": 1, "emoji": "🍻"},
    {"nome": "Assist", "punti": 2, "emoji": "🎯"},
    {"nome": "Over 30 età", "punti": 2, "emoji": "👩‍🦳"},
    {"nome": "Under 20 età", "punti": 1, "emoji": "👧"},
    {"nome": "Straniera", "punti": 2, "emoji": "🌍"},
    {"nome": "Dormi da lei", "punti": 3.5, "emoji": "🛏️"},
    {"nome": "Sotto i due cocktail", "punti": -1, "emoji": "🍸"},
    {"nome": "Sopra i tre cocktail", "punti": 0.5, "emoji": "🍹"},
    {"nome": "Over 5 cocktail", "punti": 1.5, "emoji": "🍻"},
    {"nome": "Threesome", "punti": 5, "emoji": "🍾"},
    {"nome": "Contattino", "punti": 0.5, "emoji": "📱"},
    {"nome": "Palo", "punti": -0.5, "emoji": "🥴"},
    {"nome": "Under 4 di mattina", "punti": 0.5, "emoji": "🌅"},
    {"nome": "Oggetto rubato", "punti": 0.5, "emoji": "🕵️‍♂️"},
    {"nome": "Fermato sbirri", "punti": -1, "emoji": "👮‍♂️"},
    {"nome": "Ex", "punti": -2, "emoji": "💔"},
    {"nome": "Tornare con ex per punti", "punti": -4, "emoji": "🚫"},
    {"nome": "Mancata foto piccione a letto", "punti": -1, "emoji": "📸"},
    {"nome": "Rissa vinta", "punti": 2, "emoji": "🥊"},
    {"nome": "Rissa persa", "punti": -4, "emoji": "🤕"},
    {"nome": "Imbosco barista", "punti": 2, "emoji": "🍺"},
    {"nome": "Uscita piazza Francavilla", "punti": -0.5, "emoji": "🏞️"},
    {"nome": "Rimorchio in spiaggia", "punti": 1, "emoji": "🏖️"},
    {"nome": "Sesso con due ragazze", "punti": 8, "emoji": "🔥"},
    {"nome": "Numero senza chiedere", "punti": 2.5, "emoji": "📞"},
    {"nome": "Nessun contatto per una settimana", "punti": -3, "emoji": "📴"},
    {"nome": "Storia inventata o stravolta", "punti": -3, "emoji": "🤥"},
    {"nome": "Maleducazione/fuoriluogo", "punti": -2, "emoji": "😡"},
    {"nome": "Ghost nuova ragazza dopo 24h", "punti": -2, "emoji": "👻"},
    {"nome": "Referenze ragazze", "punti": 4, "emoji": "🏆"},
    {"nome": "Rimorchio lingua straniera", "punti": 1, "emoji": "🗣️"},
    {"nome": "Uscita settimanale (lun-gio)", "punti": 0.5, "emoji": "📅"},
    {"nome": "Chiacchierata 5 minuti", "punti": 0.5, "emoji": "💬"},
    {"nome": "Invitato post serata/mare", "punti": 1, "emoji": "🌊"},
    {"nome": "Complimenti outfit", "punti": 0.5, "emoji": "👗"},
    {"nome": "Assenza cena gruppo", "punti": -1.5, "emoji": "🍽️"},
    {"nome": "Colazione domenica mattina", "punti": 1, "emoji": "☕"},
    {"nome": "Sveglia over 15", "punti": -2, "emoji": "🛌"},
    {"nome": "Ragazza fidanzata bacio", "punti": 5, "emoji": "💋"},
    {"nome": "Restare a casa weekend", "punti": -3, "emoji": "🏠"},
    {"nome": "Ghostare ragazza interessata", "punti": -1.5, "emoji": "👻"},
]

# Storico azioni per ogni giocatore
storico_azioni = {amico['nome']: [] for amico in amici}


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/giocatori')
def giocatori():
    return render_template('giocatori.html', amici=amici)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', errore='Credenziali errate.')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome_giocatore = request.form['giocatore']
        azione_idx = int(request.form['azione'])
        azione = azioni_possibili[azione_idx]
        storico_azioni[nome_giocatore].append(azione)
        return redirect(url_for('admin'))

    return render_template('admin.html', amici=amici, azioni=azioni_possibili)

def calcola_punteggi_settimana():
    for amico in amici:
        nome = amico['nome']
        azioni = storico_azioni.get(nome, [])
        totale_settimana = sum(a['punti'] for a in azioni)
        amico['punti'] += totale_settimana

        # svuota lo storico dopo aver calcolato la settimana
        storico_azioni[nome] = []

    global settimana_corrente
    settimana_corrente += 1

@app.route('/live')
def live():
    giocatori_azioni = []
    for amico in amici:
        nome = amico['nome']
        azioni = storico_azioni.get(nome, [])
        totale = sum(a['punti'] for a in azioni)
        giocatori_azioni.append({
            "nome": nome,
            "azioni": azioni,
            "totale": totale
        })

    return render_template('live.html', giocatori=giocatori_azioni)
@app.route('/admin/calcola_settimana', methods=['POST'])
def admin_calcola_settimana():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    calcola_punteggi_settimana()
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=True)
