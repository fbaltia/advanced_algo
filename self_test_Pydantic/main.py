from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class Utilisateur(BaseModel):
    id: int = Field(..., description="Identifiant unique de l'utilisateur")
    nom: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., description="Adresse email basique")
    est_actif: bool = True
    tags: List[str] = []
    date_inscription: Optional[datetime] = None

    @field_validator('email')
    @classmethod
    def valider_email(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("L'adresse email doit contenir un '@'")
        return v.lower()


print("=== 1. CRÉATION D'OBJET & VALIDATION RÉUSSIE ===")
donnees_valides = {
    "id": 42,
    "nom": "Alice",
    "email": "Alice@Demo.com",
    "tags": ["admin", "dev"],
    "date_inscription": "2026-08-05T12:00:00"
}

user = Utilisateur(**donnees_valides)
print(f"Objet créé avec succès : {user}")
print(f"Type de date_inscription : {type(user.date_inscription)}")
print(f"Email normalisé via validateur : {user.email}\n")



# print("=== 2. SÉRIALISATION (OBJET -> DONNÉES) ===")
# print("Export en dict :", user.model_dump())
# print("Export en JSON :", user.model_dump_json())
# print()


# print("=== 3. CAPTURE DES ERREURS DE VALIDATION ===")
# donnees_invalides = {
#     "id": "pas-un-nombre",    # Erreur : attend un entier
#     "nom": "A",               # Erreur : trop court (minimum 2 caractères)
#     "email": "adresse_sans_at" # Erreur : rejeté par notre validateur personnalisé
# }

# try:
#     Utilisateur(**donnees_invalides)
# except Exception as e:
#     print(e)