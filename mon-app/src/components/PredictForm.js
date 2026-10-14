import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  MenuItem,
  TextField,
  Typography,
  Select,
  FormControl,
  InputLabel,
  Alert,
  Stepper,
  Step,
  StepLabel,
  InputAdornment,
  Checkbox,
  FormControlLabel
} from "@mui/material";




const BINARY_FIELDS_BY_TYPE = {
  appart: ["Terrasse", "Parking", "Sécurité", "Ascenseur", "Balcon", "Chauffage",
           "Climatisation", "Cuisine équipée", "Concierge", "Meublé", "Duplex"],
  maison: ["Terrasse", "Parking", "Sécurité", "Balcon", "Chauffage",
           "Climatisation", "Cuisine équipée", "Meublé", "Garage", "Jardin", "Piscine"],
  villa: ["Terrasse", "Parking", "Sécurité", "Balcon", "Chauffage",
          "Climatisation", "Cuisine équipée", "Meublé", "Garage", "Jardin", "Piscine"],
  terrain: ["Loti", "Titré"],
  bureaux: ["Terrasse", "Parking", "Sécurité", "Ascenseur", "Chauffage", "Climatisation"],
  local: ["Parking", "Chauffage", "Climatisation"]
};


const ZONING_OPTIONS = {
  "Agricole": 0,
  "Industriel": 1,
  "Immeuble": 2,
  "Maison": 3,
  "Villa": 4,
  "Service public": 5
};

const TYPE_LABELS = {
  appart: "Appartement",
  maison: "Maison",
  villa: "Villa",
  terrain: "Terrain",
  bureaux: "Bureaux",
  local: "Local"
};

const CATEGORY_LABELS = {
  Condition_encoded: "Condition",
  Standing_encoded: "Standing",
  Age_encoded: "Âge"
};

const CATEGORY_OPTIONS = {
  Condition_encoded: { "Neuf": 0, "Bon état": 1, "à rénover": 2 },
  Standing_encoded: { "Economique": 0, "Moyen standing": 1, "Haut standing": 2 },
  Age_encoded: {
    "Moins de 1 an": 0,
    "1-5 ans": 1,
    "6-10 ans": 2,
    "11-20 ans": 3,
    "21+ ans": 4
  }
};

const NUMERIC_FIELDS = ["Chambres", "Salles De Bain", "Salons", "Etage"];

const FIELDS_BY_TYPE = {
  appart: [
    "Surface Totale", "Surface Habitable", "Chambres", "Salles De Bain", "Salons", "Etage",
    ...BINARY_FIELDS_BY_TYPE.appart, "Condition_encoded", "Standing_encoded", "Age_encoded", "Ville", "Quartier"
  ],
  maison: [
    "Surface Totale", "Surface Habitable", "Chambres", "Salles De Bain", "Salons",
    ...BINARY_FIELDS_BY_TYPE.maison,
    "Condition_encoded", "Standing_encoded", "Age_encoded", "Ville", "Quartier"
  ],
  villa: [
    "Surface Totale", "Surface Habitable", "Chambres", "Salles De Bain", "Salons",
    ...BINARY_FIELDS_BY_TYPE.villa,
    "Condition_encoded", "Standing_encoded", "Age_encoded", "Ville", "Quartier"
  ],
  terrain: [
    "Surface Totale", "Loti", "Titré", "Zoning_enc", "Ville", "Quartier"
  ],
  bureaux: [
    "Surface Totale", "Salles De Bain", "Etage", ...BINARY_FIELDS_BY_TYPE.bureaux,
     "Age_encoded", "Condition_encoded", "Ville", "Quartier"
  ],
  local: [
    "Surface Totale", "Salles De Bain", ...BINARY_FIELDS_BY_TYPE.local,
    "Age_encoded", "Standing_encoded", "Ville", "Quartier"
  ]
};  

const PredictForm = () => {
  const [propertyType, setPropertyType] = useState("");
  const [formData, setFormData] = useState({});
  const [result, setResult] = useState("");
  const [villeOptions, setVilleOptions] = useState([]);
  const [quartierOptions, setQuartierOptions] = useState([]);
  const [activeStep, setActiveStep] = useState(0);

  const steps = ["Type", "Ville & Quartier", "Surfaces", "Détails", "Équipements & Commodités", "État du bien", "Confirmation"];

  const [isConfirmed, setIsConfirmed] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleReset = () => {
    setFormData({});
    setPropertyType("");
    setActiveStep(0);
    setResult("");
    setIsConfirmed(false);
    setVilleOptions([]);
    setQuartierOptions([]);
  };

  const validateSurfaceFields = () => {
    const surfaceTotale = Number(formData["Surface Totale"]);
    const surfaceHabitable = Number(formData["Surface Habitable"]);

    if (!isNaN(surfaceTotale) && !isNaN(surfaceHabitable)) {
      return surfaceHabitable <= surfaceTotale;
    }
    return true; // Ne bloque pas si une des deux valeurs est manquante
  };

  useEffect(() => {
    if (propertyType) {
      fetch(`http://localhost:5000/villes?type=${propertyType}`)
        .then(res => res.json())
        .then(data => setVilleOptions(data))
        .catch(() => setVilleOptions([]));
    }
  }, [propertyType]);

  useEffect(() => {
    if (propertyType && formData["Ville"]) {
      fetch(`http://localhost:5000/quartiers?type=${propertyType}&ville=${formData["Ville"]}`)
        .then(res => res.json())
        .then(data => setQuartierOptions(data))
        .catch(() => setQuartierOptions([]));
    }
  }, [propertyType, formData["Ville"]]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    let val = value;

    if (name === "Zoning_enc") {
      val = ZONING_OPTIONS[value];
    } else if (CATEGORY_OPTIONS[name]) {
      val = CATEGORY_OPTIONS[name][value];
    } else if (!isNaN(value) && typeof value === "string" && value.trim() !== "") {
      val = Number(value);
    }

    setFormData(prev => ({ ...prev, [name]: val }));
  };

  const handleStepClick = (index) => setActiveStep(index);
  const handleNext = () => setActiveStep(prev => prev + 1);
  const handleBack = () => setActiveStep(prev => prev - 1);

  const handleSubmit = async (e) => {
  e.preventDefault();
  setResult("");
  setLoading(true);

  try {
    const response = await fetch("http://localhost:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: propertyType, features: formData })
    });

    const data = await response.json();
    setResult(
      data.predicted_price
        ? `✅ Prix estimé : ${data.predicted_price.toLocaleString()} MAD`
        : `❌ Erreur : ${data.error}`
    );

    // ✅ Réinitialisation si succès
    if (data.predicted_price) {
      
    }
  } catch (error) {
    setResult("❌ Une erreur s'est produite. Veuillez réessayer.");
  } finally {
    setLoading(false);
  }
};



  const currentFields = propertyType ? FIELDS_BY_TYPE[propertyType] : [];
  const visibleFields = currentFields.filter(field => {
    if (activeStep === 0) return false;
    if (activeStep === 1) return ["Ville", "Quartier"].includes(field);
    if (activeStep === 2) return field.toLowerCase().includes("surface");
    if (activeStep === 3) {
      if (propertyType === "terrain") return ["Zoning_enc"].includes(field);
      return NUMERIC_FIELDS.includes(field);
    }
    if (activeStep === 4) {
      const allowedFields = BINARY_FIELDS_BY_TYPE[propertyType] || [];
      return allowedFields.includes(field);
    }
    if (activeStep === 5) return CATEGORY_OPTIONS[field];
    return false;
  });

  return (
    <Box sx={{ maxWidth: 700, mx: "auto", my: 4, p: 3, boxShadow: 3, borderRadius: 2 }}>
      <Box sx={{ textAlign: "center", py: 2, mb: 3, background: "linear-gradient(to right, #2193b0, #6dd5ed)", color: "white", borderRadius: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: "bold" }}>Estimation d’un bien immobilier</Typography>
      </Box>

      <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 3, "& .MuiStepLabel-label": { fontWeight: "bold" }, "& .MuiStepIcon-root.Mui-active": { color: "#1976d2" }, "& .MuiStepIcon-root.Mui-completed": { color: "#4caf50" } }}>
        {steps.map((label, index) => (
          <Step key={label} onClick={() => handleStepClick(index)}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {activeStep === 0 && (
        <FormControl fullWidth variant="outlined">
          <InputLabel>Type de bien</InputLabel>
          <Select value={propertyType} label="Type de bien" onChange={(e) => { setPropertyType(e.target.value); setFormData({}); setResult(""); }}>
            <MenuItem value="">-- Choisir --</MenuItem>
            {Object.keys(FIELDS_BY_TYPE).map((type) => (
              <MenuItem key={type} value={type}>{TYPE_LABELS[type] || type}</MenuItem>
            ))}
          </Select>
        </FormControl>
      )}

      {propertyType && activeStep > 0 && (
        <form onSubmit={handleSubmit}>
          {activeStep === steps.length - 1 ? (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>📝 Vérifiez les informations saisies :</Typography>
              {Object.entries(formData).map(([key, value]) => (
                <Typography key={key} sx={{ my: 1 }}>
                  <strong>{CATEGORY_LABELS[key] || key} :</strong>{" "}
                  {ZONING_OPTIONS && key === "Zoning_enc"
                    ? Object.keys(ZONING_OPTIONS).find(k => ZONING_OPTIONS[k] === value)
                    : CATEGORY_OPTIONS[key]
                      ? Object.keys(CATEGORY_OPTIONS[key]).find(k => CATEGORY_OPTIONS[key][k] === value)
                      : typeof value === "boolean"
                        ? value ? "Oui" : "Non"
                        : value?.toString()}
                </Typography>
              ))}
            </Box>
          ) : visibleFields.map((field) => {
            const label = CATEGORY_LABELS[field] || field;
            const isNumeric = NUMERIC_FIELDS.includes(field);
            const isSurface = field.toLowerCase().includes("surface");
            const value = formData[field] !== undefined ? formData[field] : "";
            const options = field === "Ville" ? villeOptions : field === "Quartier" ? quartierOptions : [];

            if (["Ville", "Quartier"].includes(field)) {
              return (
                <TextField key={field} fullWidth margin="normal" select name={field} label={label} value={value} onChange={handleInputChange} required>
                  <MenuItem value="">-- Choisir {field.toLowerCase()} --</MenuItem>
                  {options.map((option) => (
                    <MenuItem key={option} value={option}>{option}</MenuItem>
                  ))}
                </TextField>
              );
            }

            if (field === "Zoning_enc") {
              return (
                <TextField key={field} fullWidth margin="normal" select name={field} label="Zonage" value={Object.keys(ZONING_OPTIONS).find(k => ZONING_OPTIONS[k] === value) || ""} onChange={handleInputChange} required>
                  <MenuItem value="">-- Choisir --</MenuItem>
                  {Object.keys(ZONING_OPTIONS).map((zone) => (
                    <MenuItem key={zone} value={zone}>{zone}</MenuItem>
                  ))}
                </TextField>
              );
            }

            if (CATEGORY_OPTIONS[field]) {
              return (
                <TextField key={field} fullWidth margin="normal" select name={field} label={label} value={Object.keys(CATEGORY_OPTIONS[field]).find(k => CATEGORY_OPTIONS[field][k] === value) || ""} onChange={handleInputChange} required>
                  <MenuItem value="">-- Choisir --</MenuItem>
                  {Object.keys(CATEGORY_OPTIONS[field]).map((option) => (
                    <MenuItem key={option} value={option}>{option}</MenuItem>
                  ))}
                </TextField>
              );
            }

            if ((BINARY_FIELDS_BY_TYPE[propertyType] || []).includes(field)) {
              return (
                <TextField key={field} fullWidth margin="normal" select name={field} label={label} value={value} onChange={handleInputChange} required>
                  <MenuItem value="">-- Choisir --</MenuItem>
                  <MenuItem value={1}>Oui</MenuItem>
                  <MenuItem value={0}>Non</MenuItem>
                </TextField>
              );
            }

            return (
              <TextField key={field} fullWidth margin="normal" variant="outlined" type={isNumeric ? "number" : "text"} name={field} label={label} value={value} onChange={handleInputChange} inputProps={isNumeric ? { min: 0, step: 1 } : {}} required InputProps={isSurface ? { endAdornment: <InputAdornment position="end">m²</InputAdornment> } : {}} />
            );
          })}

          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 2 }}>
  {activeStep > 0 && (
    <Box sx={{ display: "flex", justifyContent: "space-between" }}>
      <Button onClick={handleBack}>Retour</Button>
      {activeStep < steps.length - 1 ? (
        <Button
          variant="contained"
          onClick={handleNext}
          disabled={
            !propertyType || 
            (activeStep === 2 && !validateSurfaceFields())
          }
        >
          Suivant
        </Button>
      ) : (
        <></> // rien ici, le bloc suivant s'affiche
      )}
    </Box>
  )}

  {activeStep === steps.length - 1 && (
    <>
      <FormControlLabel
        control={
          <Checkbox
            checked={isConfirmed}
            onChange={(e) => setIsConfirmed(e.target.checked)}
            color="primary"
          />
        }
        label="Je confirme que les informations saisies sont exactes"
      />

      <Button
        variant="contained"
        color="primary"
        type="submit"
        disabled={!isConfirmed || loading}
        sx={{
          transition: "0.3s",
          "&:hover": {
            transform: "scale(1.05)",
            boxShadow: 6
          }
        }}
      >
        {loading ? "Calcul..." : "Prédire"}
      </Button>
    </>
  )}
</Box>

        </form>
      )}

      {result && (
        <>
          <Alert
            severity={result.includes("✅") ? "success" : result.includes("⏳") ? "info" : "error"}
            sx={{ mt: 3, fontSize: "1.1rem", fontWeight: "bold", py: 2 }}
          >
            {result}
          </Alert>

          <Box sx={{ mt: 2, textAlign: "center" }}>
            <Button variant="outlined" color="secondary" onClick={handleReset}>
              Réinitialiser le formulaire
            </Button>
          </Box>
      </>
      )}
    </Box>
  );
};

export default PredictForm;
