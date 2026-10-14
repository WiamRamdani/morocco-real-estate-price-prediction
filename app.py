import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS

# ✅ Configurations par type de bien
CONFIG = {
    "appart": {
        "model_path": "models/model_appart.pkl",
        "features": [
            'Surface Totale', 'Surface Habitable', 'Chambres', 'Salles De Bain',
            'Salons', 'Etage', 'Terrasse', 'Parking', 'Sécurité', 'Ascenseur',
            'Balcon', 'Chauffage', 'Climatisation', 'Cuisine équipée', 'Concierge',
            'Meublé', 'Duplex', 'Condition_encoded', 'Standing_encoded',
            'Age_encoded', 'Quartier_enc'
        ]
    },
    "maison": {
        "model_path": "models/model_maison.pkl",
        "features": [
            'Surface Totale', 'Surface Habitable', 'Chambres', 'Salles De Bain',
            'Salons', 'Terrasse', 'Parking', 'Sécurité', 'Balcon', 'Chauffage',
            'Climatisation', 'Cuisine équipée', 'Meublé', 'Garage', 'Jardin',
            'Piscine', 'Condition_encoded', 'Standing_encoded', 'Age_encoded',
            'Quartier_enc'
        ]
    },
    "terrain": {
        "model_path": "models/model_terrain.pkl",
        "features": [
            'Surface Totale', 'Loti', 'Titré', 'Zoning_enc',
            'Quartier_enc'
        ]
    },
    "villa": {
        "model_path": "models/model_villa.pkl",
        "features": [
            'Surface Totale', 'Surface Habitable', 'Chambres', 'Salles De Bain',
            'Salons', 'Terrasse', 'Parking', 'Sécurité', 'Balcon', 'Chauffage',
            'Climatisation', 'Cuisine équipée', 'Meublé', 'Garage', 'Jardin',
            'Piscine', 'Condition_encoded', 'Standing_encoded', 'Age_encoded',
            'Quartier_enc'
        ]
    },
    "bureaux": {
        "model_path": "models/model_bureaux.pkl",
        "features": [
            'Surface Totale', 'Salles De Bain', 'Etage', 'Terrasse', 'Parking',
            'Sécurité', 'Chauffage', 'Climatisation', 'Ascenseur', 'Age_encoded',
            'Condition_encoded', 'Quartier_enc'
        ]
    },
    "local": {
        "model_path": "models/model_local.pkl",
        "features": [
            'Surface Totale', 'Salles De Bain', 'Parking', 'Chauffage',
            'Climatisation', 'Age_encoded', 'Standing_encoded', 'Quartier_enc'
        ]
    }
}

datasets = {
    prop_type: pd.read_csv(f"{prop_type}/FinalDataSet_{prop_type}.csv")
    for prop_type in CONFIG
}

# ✅ Charger le modèle selon le type de bien
def load_model(property_type):
    conf = CONFIG.get(property_type)
    if not conf:
        raise ValueError(f"[❌] Type de bien inconnu : {property_type}")
    with open(conf["model_path"], 'rb') as f:
        return joblib.load(f)

# ✅ Préparer l'input pour la prédiction
def prepare_input(user_input, df, property_type):
    conf = CONFIG.get(property_type)
    if not conf:
        raise ValueError(f"[❌] Type de bien non configuré : {property_type}")
    used_features = conf["features"]

    # 1. Encodage Quartier
    quartier_mean_mapping = df.groupby("Quartier")["Prix"].mean().to_dict()
    global_mean = df["Prix"].mean()
    quartier_enc = quartier_mean_mapping.get(user_input.get("Quartier", ""), global_mean)
    user_input["Quartier_enc"] = quartier_enc

    # 2. Ville & dummies
    ville_value = user_input.get("Ville", "Autres")
    del user_input["Ville"]
    if "Quartier" in user_input:
        del user_input["Quartier"]

    # 3. Dummies ville
    ville_dummies = [col for col in df.columns if col.startswith("Ville_")]
    ville_dummies_input = dict.fromkeys(ville_dummies, 0)
    ville_col = f"Ville_{ville_value}"
    if ville_col in ville_dummies:
        ville_dummies_input[ville_col] = 1
    else:
        ville_dummies_input["Ville_Autres"] = 1

    # 4. Fusion
    full_input = {**user_input, **ville_dummies_input}
    final_features = used_features + ville_dummies
    for col in final_features:
        if col not in full_input:
            full_input[col] = 0  # valeur par défaut

    # 5. Créer DataFrame
    X_new = pd.DataFrame([full_input])[final_features]
    return X_new

# === Lancer l'API Flask ===
app = Flask(__name__)
CORS(app) 

@app.route("/villes", methods=["GET"])
def get_villes():
    try:
        property_type = request.args.get("type")
        if property_type not in datasets:
            return jsonify({"error": "Type de bien non supporté"}), 400

        df = datasets[property_type]
        villes = sorted(df["Ville"].dropna().unique().tolist())
        return jsonify(villes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/quartiers", methods=["GET"])
def get_quartiers():
    try:
        property_type = request.args.get("type")
        ville = request.args.get("ville")

        if property_type not in datasets:
            return jsonify({"error": "Type de bien non supporté"}), 400
        if not ville:
            return jsonify({"error": "Ville non précisée"}), 400

        df = datasets[property_type]
        quartiers = df[df["Ville"] == ville]["Quartier"].dropna().unique().tolist()
        return jsonify(sorted(quartiers))
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/predict", methods=["POST"])
def predict():
    try:
        content = request.get_json()
        property_type = content.get("type")
        if property_type not in CONFIG:
            return jsonify({"error": "Type de bien non supporté"}), 400

        user_input = content.get("features")
        model = load_model(property_type)
        df = datasets[property_type]
        X = prepare_input(user_input, df, property_type)
        price = model.predict(X)[0]
        return jsonify({"predicted_price": round(price, 2)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)