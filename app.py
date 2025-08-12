from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'supersegretachiave'

# Configurazione DB SQLite locale
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fantacipponi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Costanti admin
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '123'

# Modelli DB
class AzioneAssegnata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    punti = db.Column(db.Integer)
    emoji = db.Column(db.String(10))
    settimana = db.Column(db.Integer)
    amico_id = db.Column(db.Integer, db.ForeignKey('amico.id'))
    amico = db.relationship('Amico', backref=db.backref('azioni_assegnate', lazy=True))


class Amico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    logo_url = db.Column(db.String(200), nullable=True)
    punti = db.Column(db.Float, default=0)

    azioni = db.relationship('Azione', backref='amico_catalogo', lazy=True) # Changed backref to avoid conflict

class Azione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    punti = db.Column(db.Float, nullable=False)
    emoji = db.Column(db.String(10), nullable=True)
    settimana = db.Column(db.Integer, nullable=True)
    amico_id = db.Column(db.Integer, db.ForeignKey('amico.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Lista azioni possibili (fissa, potresti anche creare tabella separata se vuoi)
azioni_possibili = [
    {"nome": "Serata giocata", "punti": 1, "emoji": "🎉"},
    {"nome": "Serata non giocata", "punti": 0, "emoji": "😴"},
    {"nome": "Sboccata", "punti": -1, "emoji": "🤮"},
    {"nome": "Chi guida", "punti": 3, "emoji": "🚗"},
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

# FILE DI PERSISTENZA
DATA_FILE = 'dati.json'

# === Funzioni di PERSISTENZA ===
def carica_dati():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        'punteggi': {},
        'azioni_settimanali': {},
        'settimana_corrente': 1
    }

def salva_dati(dati):
    with open(DATA_FILE, 'w') as f:
        json.dump(dati, f, indent=4)

# Carica i dati all'avvio
dati = carica_dati()
settimana_corrente = dati.get('settimana_corrente', 1)


@app.route('/')
def home():
    return render_template('home.html')

#@app.route('/giocatori')
#def giocatori():
    #amici = Amico.query.all()
    #for amico in amici:
        #amico.punti = sum(a.punti for a in amico.azioni_assegnate)
    #db.session.commit()
    #return render_template('giocatori.html', amici=amici)
@app.route('/giocatori')
def giocatori():
    amici = Amico.query.order_by(Amico.punti.desc()).all() # Ordina per punti decrescenti
    return render_template('giocatori.html', amici=amici)

@app.route('/giocatore/<int:amico_id>')
def dettaglio_giocatore(amico_id):
    amico = Amico.query.get_or_404(amico_id)
    azioni_per_settimana = {}

    azioni_assegnate = AzioneAssegnata.query.filter_by(amico_id=amico.id).order_by(AzioneAssegnata.settimana).all()
    for azione in azioni_assegnate:
        azioni_per_settimana.setdefault(azione.settimana, []).append(azione)

    return render_template('giocatore_storico.html', nome=amico.nome, azioni_per_settimana=azioni_per_settimana)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Login effettuato con successo!', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Credenziali errate.', 'error')
            return render_template('login.html', errore='Credenziali errate.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logout effettuato.', 'info')
    return redirect(url_for('home'))

@app.route('/admin', methods=['GET'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    amici = Amico.query.all()
    azioni_catalogo = Azione.query.all()

    return render_template(
        'admin.html',
        amici=amici,
        azioni=azioni_catalogo,
        settimana_corrente=settimana_corrente,
        amico=None,
        azioni_assegnate=[]
    )

@app.route('/admin/assegna_azione', methods=['POST'])
def assegna_azione():
    global settimana_corrente
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    amico_id = request.form.get('giocatore')
    azione_ids = request.form.getlist('azioni')

    if not amico_id:
        flash('Seleziona un giocatore.', 'error')
        return redirect(url_for('admin'))

    if not azione_ids:
        flash('Seleziona almeno un\'azione.', 'error')
        return redirect(url_for('admin'))

    try:
        amico_id = int(amico_id)
        amico = Amico.query.get(amico_id)

        if not amico:
            flash('Giocatore non trovato.', 'error')
            return redirect(url_for('admin'))

        azioni_assegnate_count = 0
        for az_id in azione_ids:
            try:
                azione_catalogo = Azione.query.get(int(az_id))
                if azione_catalogo:
                    nuova_azione = AzioneAssegnata(
                        nome=azione_catalogo.nome,
                        punti=azione_catalogo.punti,
                        emoji=azione_catalogo.emoji,
                        settimana=settimana_corrente,
                        amico=amico
                    )
                    db.session.add(nuova_azione)
                    azioni_assegnate_count += 1
            except ValueError:
                flash(f'ID azione "{az_id}" non valido e ignorato.', 'warning')
                continue

        db.session.commit()
        if azioni_assegnate_count > 0:
            flash(f'{azioni_assegnate_count} azione(i) assegnata(e) a {amico.nome} per la settimana {settimana_corrente}.', 'success')
        else:
            flash('Nessuna azione valida selezionata o assegnata.', 'info')

    except ValueError:
        flash('ID giocatore non valido.', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Si è verificato un errore durante l\'assegnazione delle azioni: {e}', 'error')

    return redirect(url_for('admin'))

@app.route('/admin/calcola_settimana', methods=['POST'])
def admin_calcola_settimana():
    global settimana_corrente, dati
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    amici = Amico.query.all()
    for amico in amici:
        azioni_settimana_assegnate = AzioneAssegnata.query.filter_by(amico_id=amico.id, settimana=settimana_corrente).all()
        totale_settimana = sum(a.punti for a in azioni_settimana_assegnate)
        amico.punti += totale_settimana

    settimana_corrente += 1
    dati['settimana_corrente'] = settimana_corrente
    salva_dati(dati)

    db.session.commit()
    flash(f'Punteggi della settimana {settimana_corrente - 1} calcolati. Nuova settimana corrente: {settimana_corrente}.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/aggiorna_settimana', methods=['POST'])
def admin_aggiorna_settimana():
    global settimana_corrente, dati
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        nuova_settimana = int(request.form['settimana_corrente'])
        if nuova_settimana < 1:
            flash('La settimana deve essere almeno 1.', 'error')
            return redirect(url_for('admin'))
        settimana_corrente = nuova_settimana
        dati['settimana_corrente'] = settimana_corrente
        salva_dati(dati)
        flash(f'Settimana corrente aggiornata a {settimana_corrente}.', 'success')
    except ValueError:
        flash('Valore della settimana non valido.', 'error')
    return redirect(url_for('admin'))

@app.route('/admin/giocatore/<int:amico_id>/azioni', methods=['GET', 'POST'])
def admin_modifica_azioni(amico_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    amico = Amico.query.get_or_404(amico_id)
    azioni_assegnate = AzioneAssegnata.query.filter_by(amico_id=amico_id).order_by(AzioneAssegnata.settimana).all()

    if request.method == 'POST':
        action = request.form['action']
        azione_id = int(request.form['azione_id'])

        azione = AzioneAssegnata.query.get_or_404(azione_id)

        if action == 'delete':
            db.session.delete(azione)
            flash(f'Azione "{azione.nome}" eliminata per {amico.nome}.', 'success')
        elif action == 'sposta':
            try:
                nuova_settimana = int(request.form['nuova_settimana'])
                if nuova_settimana < 1:
                    flash('La settimana deve essere almeno 1.', 'error')
                else:
                    azione.settimana = nuova_settimana
                    flash(f'Azione "{azione.nome}" spostata alla settimana {nuova_settimana}.', 'success')
            except ValueError:
                flash('Valore della settimana non valido.', 'error')
        db.session.commit()
        return redirect(url_for('admin_modifica_azioni', amico_id=amico_id))

    return render_template('admin_modifica_azioni.html', amico=amico, azioni_assegnate=azioni_assegnate, settimana_corrente=settimana_corrente)

@app.route('/admin/reset', methods=['POST'])
def admin_reset():
    global settimana_corrente, dati

    if not session.get('logged_in'):
        return redirect(url_for('login'))

    amici = Amico.query.all()
    for amico in amici:
        amico.punti = 0

    AzioneAssegnata.query.delete()

    settimana_corrente = 1
    dati['settimana_corrente'] = settimana_corrente
    
    # Aggiungi questa riga per resettare il file dati.json
    salva_dati(dati) 
    
    db.session.commit()
    flash('Gioco resettato con successo!', 'success')
    return redirect(url_for('admin'))

def calcola_quote_live():
    amici = Amico.query.all()
    if not amici:
        return {}

    total_punti = sum(amico.punti for amico in amici)

    quote_live = {}
    if total_punti == 0:
        num_amici = len(amici)
        if num_amici > 0:
            quota_base = 3.0
            for amico in amici:
                quote_live[amico.nome] = f"{quota_base:.2f}"
    else:
        punti_min = min(amico.punti for amico in amici)
        punti_max = max(amico.punti for amico in amici)
        punti_range = punti_max - punti_min
        if punti_range == 0:
            quota_media = 3.5
            for amico in amici:
                quote_live[amico.nome] = f"{quota_media:.2f}"
        else:
            quota_minima_desiderata = 1.5
            quota_massima_desiderata = 8.0

            for amico in amici:
                if punti_range == 0:
                    normalized_punti = 0.5
                else:
                    normalized_punti = (amico.punti - punti_min) / punti_range
                quota = (1 - normalized_punti) * (
                            quota_massima_desiderata - quota_minima_desiderata) + quota_minima_desiderata
                quote_live[amico.nome] = f"{quota:.2f}"

    return quote_live

@app.route('/quote')
def quote():
    quote_partenza = {
        "ALESSANDRO SPINA": 4.50,
        "FEDERICO CONTE": 2.20,
        "GIAMBURRASCA": 3.40,
        "AURELIO CARROZZO": 3.60,
        "FRANCESCO CARROZZO": 3.50,
        "FRANCESCO DENUZZO": 5.90,
        "ANDREA CARONE": 4.50,
        "DOMENICO MAZZA": 1.60,
    }

    quote_live = calcola_quote_live()

    return render_template('quote.html',
                           quote_partenza=quote_partenza,
                           quote_live=quote_live)

@app.route('/regolamento_premi')
def regolamento_premi():
    return render_template('regolamento_premi.html')

@app.route('/live')
def live():
    amici = Amico.query.all()
    giocatori_azioni = []

    for amico in amici:
        azioni = AzioneAssegnata.query.filter_by(amico_id=amico.id, settimana=settimana_corrente).all()
        totale = sum(a.punti for a in azioni)
        giocatori_azioni.append({
            'nome': amico.nome,
            'punti_settimana': totale,
            'azioni_per_settimana': {settimana_corrente: azioni}
        })
    return render_template('live.html', giocatori=giocatori_azioni, settimana_corrente=settimana_corrente)

def popola_amici():
    amici_lista = [
        {"nome": "Alessandro Spina", "logo_url": "/static/Alessandro.jpg"},
        {"nome": "Federico Conte", "logo_url": "/static/loghi/federico.jpg"},
        {"nome": "Giamburrasca", "logo_url": "/static/loghi/giamburrasca.png"},
        {"nome": "Aurelio Carrozzo", "logo_url": "/static/loghi/aurelio_carrozzo.png"},
        {"nome": "Francesco Carrozzo", "logo_url": "/static/loghi/francesco_carrozzo.png"},
        {"nome": "Francesco Denuzzo", "logo_url": "/static/loghi/francesco_denuzzo.png"},
        {"nome": "Andrea Carone", "logo_url": "/static/loghi/birillo.jpg"},
        {"nome": "Domenico Mazza", "logo_url": "/static/loghi/domenico_mazza.png"}
    ]
    for a in amici_lista:
        esistente = Amico.query.filter_by(nome=a['nome']).first()
        if not esistente:
            nuovo_amico = Amico(nome=a['nome'], logo_url=a['logo_url'])
            db.session.add(nuovo_amico)
    db.session.commit()

def popola_azioni_catalogo():
    if Azione.query.first() is None:
        for az in azioni_possibili:
            nuova_azione = Azione(
                nome=az['nome'],
                punti=az['punti'],
                emoji=az['emoji'],
                settimana=0,
                amico_id=None
            )
            db.session.add(nuova_azione)
        db.session.commit()
        print("Catalogo azioni popolato.")
    else:
        print("Catalogo già esistente.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        popola_amici()
        popola_azioni_catalogo()
    app.run(debug=True)
