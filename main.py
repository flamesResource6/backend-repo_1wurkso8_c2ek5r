import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import (
    MenuItem,
    CanteenMenuDay,
    TimetableEntry,
    AbsenceRecord,
    PronoteCredentials,
)

app = FastAPI(title="Lycée Charles de Gaulle API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend Lycée Charles de Gaulle opérationnel"}

@app.get("/api/hello")
def hello():
    return {"message": "Bienvenue sur l'API du Lycée Charles de Gaulle"}

@app.get("/test")
def test_database():
    """Test pour vérifier la connexion base de données"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# ---------------- CANTINE (MENU) ----------------

class MenuCreate(CanteenMenuDay):
    pass

class MenuOut(BaseModel):
    id: str
    date: str
    items: List[MenuItem]

from bson import ObjectId

def _serialize_menu(doc) -> MenuOut:
    return MenuOut(
        id=str(doc.get("_id")),
        date=doc.get("date"),
        items=[MenuItem(**item) for item in doc.get("items", [])],
    )

@app.post("/api/menu", response_model=dict)
def create_menu_day(payload: MenuCreate):
    """Créer/enregistrer le menu d'un jour (réservé administration)"""
    try:
        inserted_id = create_document("canteenmenuday", payload)
        return {"success": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu/today", response_model=Optional[MenuOut])
def get_today_menu():
    """Obtenir le menu d'aujourd'hui"""
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        docs = get_documents("canteenmenuday", {"date": today}, limit=1)
        if not docs:
            return None
        return _serialize_menu(docs[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu", response_model=List[MenuOut])
def get_menu_range(start: str = Query(..., description="YYYY-MM-DD"), end: str = Query(..., description="YYYY-MM-DD")):
    """Obtenir les menus entre deux dates incluses"""
    try:
        docs = get_documents("canteenmenuday", {"date": {"$gte": start, "$lte": end}}, limit=100)
        return [_serialize_menu(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- PRONOTE (EMPLOI DU TEMPS & ABSENCES) ----------------
# Remarque: Pour une intégration réelle, utiliser la librairie pronotepy côté serveur.
# Ici, on renvoie des données simulées pour valider le flux bout-en-bout.

class TimetableRequest(PronoteCredentials):
    start: Optional[str] = None  # YYYY-MM-DD
    end: Optional[str] = None

@app.post("/api/pronote/timetable", response_model=List[TimetableEntry])
def get_pronote_timetable(req: TimetableRequest):
    """Récupère l'emploi du temps via Pronote (simulation)"""
    try:
        # Simulation: on génère 5 cours entre les dates demandées
        start_date = datetime.utcnow().date()
        end_date = start_date
        if req.start:
            start_date = datetime.strptime(req.start, "%Y-%m-%d").date()
        if req.end:
            end_date = datetime.strptime(req.end, "%Y-%m-%d").date()
        if end_date < start_date:
            end_date = start_date
        results: List[TimetableEntry] = []
        cur = start_date
        subjects = ["Maths", "Français", "Physique", "Histoire", "Anglais"]
        rooms = ["B201", "A105", "Lab1", "C303", "L001"]
        i = 0
        while cur <= end_date and i < 10:
            start_t = datetime.combine(cur, datetime.strptime("08:00", "%H:%M").time())
            end_t = start_t + timedelta(hours=1, minutes=30)
            results.append(
                TimetableEntry(
                    date=cur.strftime("%Y-%m-%d"),
                    start=start_t.strftime("%H:%M"),
                    end=end_t.strftime("%H:%M"),
                    subject=subjects[i % len(subjects)],
                    room=rooms[i % len(rooms)],
                    teacher="M./Mme X",
                    group="2nde A",
                )
            )
            cur += timedelta(days=1)
            i += 1
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AbsencesRequest(PronoteCredentials):
    start: Optional[str] = None
    end: Optional[str] = None

@app.post("/api/pronote/absences", response_model=List[AbsenceRecord])
def get_pronote_absences(req: AbsencesRequest):
    """Récupère les absences via Pronote (simulation)"""
    try:
        # Simulation: 0 ou 1 absence aléatoire sur la période
        start_date = datetime.utcnow().date()
        if req.start:
            start_date = datetime.strptime(req.start, "%Y-%m-%d").date()
        absence_day = start_date.strftime("%Y-%m-%d")
        return [
            AbsenceRecord(
                date=absence_day,
                start="10:00",
                end="12:00",
                justified=False,
                reason=None,
            )
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
