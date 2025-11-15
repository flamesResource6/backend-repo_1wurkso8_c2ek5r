"""
Database Schemas

Pydantic models defining collections used by the application.
Each model name corresponds to a MongoDB collection (lowercased).
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Core user/admin examples (kept for reference)
class User(BaseModel):
    name: str = Field(..., description="Nom complet")
    email: EmailStr = Field(..., description="Adresse email")
    address: str = Field(..., description="Adresse")
    age: Optional[int] = Field(None, ge=0, le=120, description="Âge")
    is_active: bool = Field(True, description="Actif")

class Product(BaseModel):
    title: str = Field(..., description="Titre")
    description: Optional[str] = Field(None, description="Description")
    price: float = Field(..., ge=0, description="Prix")
    category: str = Field(..., description="Catégorie")
    in_stock: bool = Field(True, description="En stock")

# Lycée app specific schemas
class MenuItem(BaseModel):
    dish: str = Field(..., description="Nom du plat")
    type: str = Field(..., description="Type (entrée, plat, dessert, végétarien, etc.)")

class CanteenMenuDay(BaseModel):
    date: str = Field(..., description="Date au format YYYY-MM-DD")
    items: List[MenuItem] = Field(default_factory=list, description="Liste des plats du jour")

class TimetableEntry(BaseModel):
    date: str = Field(..., description="Date YYYY-MM-DD")
    start: str = Field(..., description="Heure de début HH:MM")
    end: str = Field(..., description="Heure de fin HH:MM")
    subject: str = Field(..., description="Matière")
    room: Optional[str] = Field(None, description="Salle")
    teacher: Optional[str] = Field(None, description="Professeur")
    group: Optional[str] = Field(None, description="Groupe/Classe")

class AbsenceRecord(BaseModel):
    date: str = Field(..., description="Date YYYY-MM-DD")
    start: str = Field(..., description="Heure de début HH:MM")
    end: str = Field(..., description="Heure de fin HH:MM")
    justified: bool = Field(False, description="Justifiée")
    reason: Optional[str] = Field(None, description="Motif")

class PronoteCredentials(BaseModel):
    url: str = Field(..., description="URL Pronote de l'établissement")
    username: str = Field(..., description="Identifiant")
    password: str = Field(..., description="Mot de passe")
