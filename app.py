from flask import Flask, jsonify, request, render_template
app = Flask(__name__)

# --- Classi ---
class Serbatoio:
    def __init__(self, capacita, livello_iniziale=0):
        self._capacita = max(0, capacita)
        if livello_iniziale < 0:
            self._livello = 0
        elif livello_iniziale > self._capacita:
            self._livello = self._capacita
        else:
            self._livello = livello_iniziale

    def get_capacita(self):
        return self._capacita

    def get_livello(self):
        return self._livello

    def aggiungi(self, litri):
        if litri < 0:
            return 1
        if self._livello + litri > self._capacita:
            self._livello = self._capacita
            return 1
        self._livello += litri
        return 0

    def rimuovi(self, litri):
        if litri < 0:
            return 1
        if self._livello - litri < 0:
            self._livello = 0
            return 1
        self._livello -= litri
        return 0

    def riempi(self):
        self._livello = self._capacita
        return 0

class Distributore:
    def __init__(self, id_distributore, citta, provincia, lat, lon,
                 capacita_benzina, capacita_diesel,
                 num_pompe, prezzo_benzina, prezzo_diesel):
        self._id = id_distributore
        self._citta = citta
        self._provincia = provincia
        self._lat = lat
        self._lon = lon
        self._serbatoio_benzina = Serbatoio(capacita_benzina)
        self._serbatoio_diesel = Serbatoio(capacita_diesel)
        self._serbatoio_benzina.riempi()
        self._serbatoio_diesel.riempi()
        self._num_pompe = num_pompe
        self._prezzo_benzina = prezzo_benzina
        self._prezzo_diesel = prezzo_diesel

    def to_dict(self):
        return {
            "id": self._id,
            "citta": self._citta,
            "provincia": self._provincia,
            "lat": self._lat,
            "lon": self._lon,
            "benzina_litri": self._serbatoio_benzina.get_livello(),
            "diesel_litri": self._serbatoio_diesel.get_livello(),
            "prezzo_benzina": self._prezzo_benzina,
            "prezzo_diesel": self._prezzo_diesel,
            "num_pompe": self._num_pompe
        }

    def set_prezzi(self, benzina, diesel):
        self._prezzo_benzina = benzina
        self._prezzo_diesel = diesel

# --- Lista distributori ---
distributori = [
    Distributore(1, "Milano Centro", "MI", 45.4642, 9.19, 1000, 800, 4, 1.9, 1.7),
    Distributore(2, "Milano Nord", "MI", 45.52, 9.22, 950, 750, 3, 1.88, 1.68),
    Distributore(3, "Milano Sud", "MI", 45.42, 9.18, 1100, 900, 5, 1.91, 1.71),
    Distributore(4, "Rho", "MI", 45.53, 9.04, 1050, 850, 4, 1.87, 1.67),
    Distributore(5, "Sesto SG", "MI", 45.54, 9.23, 1200, 1000, 4, 1.92, 1.72),
    Distributore(6, "Monza Centro", "MB", 45.58, 9.27, 1000, 800, 4, 1.9, 1.7),
    Distributore(7, "Lissone", "MB", 45.61, 9.24, 950, 750, 3, 1.88, 1.68),
    Distributore(8, "Seregno", "MB", 45.65, 9.20, 1100, 900, 5, 1.91, 1.71),
    Distributore(9, "Desio", "MB", 45.62, 9.21, 1050, 850, 4, 1.87, 1.67),
    Distributore(10, "Vimercate", "MB", 45.62, 9.37, 1200, 1000, 4, 1.92, 1.72),
]

# --- API ENDPOINTS ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/distributori")
def api_distributori():
    return jsonify([d.to_dict() for d in sorted(distributori, key=lambda x: x._id)])

@app.route("/api/distributori/<int:id_distributore>")
def api_distributore(id_distributore):
    for d in distributori:
        if d._id == id_distributore:
            return jsonify(d.to_dict())
    return jsonify({"error": "Distributore non trovato"}), 404

@app.route("/api/distributori/provincia/<provincia>")
def api_provincia(provincia):
    filtrati = [d.to_dict() for d in distributori if d._provincia == provincia]
    return jsonify(filtrati)

@app.route("/api/distributori/prezzi/<provincia>", methods=["POST"])
def api_cambia_prezzi(provincia):
    dati = request.get_json()
    benzina = dati.get("benzina")
    diesel = dati.get("diesel")

    if benzina < 0 or diesel < 0:
        return jsonify({"error": "I prezzi non possono essere negativi"}), 400

    for d in distributori:
        if d._provincia == provincia:
            d.set_prezzi(benzina, diesel)

    return jsonify({"message": "Prezzi aggiornati"})

if __name__ == "__main__":
    app.run(debug=True)