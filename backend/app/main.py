"""EduFlow AI - Backend API principale avec FastAPI

Ce fichier contient l'API backend pour EduFlow AI qui permet:
- Génération de blocs d'apprentissage via Google Gemini
- Upload et traitement de documents (RAG)
- Création de quiz interactifs
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import os
from typing import Optional, List
import json

# Initialisation FastAPI
app = FastAPI(
    title="EduFlow AI API",
    description="Moteur d'apprentissage adaptatif avec IA",
    version="1.0.0"
)

# Configuration CORS pour le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None

# Système Prompt EduFlow AI
SYSTEM_PROMPT = """Tu es "EduFlow AI", un expert en pédagogie universitaire niveau Génie/Sciences.
Ton but: déconstruire des notions complexes en micro-blocs structurés.

STRUCTURE DE SORTIE (JSON):
{
  "titre_du_bloc": "...",
  "resume_conceptuel": "3-4 phrases vulgarisées",
  "formules_cles": ["formule1 en LaTeX", "formule2"],
  "analogie": "Comparaison vie réelle",
  "daily_5": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
  "quiz": [
    {
      "question": "...",
      "options": ["A: ...", "B: ...", "C: ...", "D: ..."],
      "correct": "B",
      "explication": "..."
    }
  ]
}

Réponds UNIQUEMENT en JSON valide, sans texte avant ou après.
"""

# Modèles de données
class GenerateDirectRequest(BaseModel):
    sujet: str
    niveau: str  # Débutant, Intermédiaire, Avancé
    objectif: str  # Examen final, Curiosité, Application pratique

class LearningBlock(BaseModel):
    titre_du_bloc: str
    resume_conceptuel: str
    formules_cles: List[str]
    analogie: str
    daily_5: List[str]
    quiz: List[dict]

# Routes API
@app.get("/")
async def root():
    return {
        "message": "EduFlow AI API",
        "version": "1.0.0",
        "ai_engine": "Google Gemini",
        "endpoints": ["/generate/direct", "/generate/upload", "/health"]
    }

@app.get("/health")
async def health_check():
    """Vérifier l'état de l'API"""
    return {
        "status": "healthy", 
        "gemini_key_configured": bool(GEMINI_API_KEY),
        "model_ready": model is not None
    }

@app.post("/api/generate/direct")
async def generate_direct(request: GenerateDirectRequest):
    """
    Génération directe via Google Gemini sans documents externes
    
    Args:
        request: Contient sujet, niveau, objectif
    
    Returns:
        LearningBlock: Bloc d'apprentissage généré
    """
    if not model:
        raise HTTPException(
            status_code=500, 
            detail="Clé API Gemini non configurée. Ajoutez GEMINI_API_KEY dans votre fichier .env"
        )
    
    try:
        prompt = f"""{SYSTEM_PROMPT}

Sujet: {request.sujet}
Niveau: {request.niveau}
Objectif: {request.objectif}

Génère un bloc d'apprentissage complet en JSON.
"""
        
        response = model.generate_content(prompt)
        
        # Extraire le JSON de la réponse
        text = response.text.strip()
        
        # Nettoyer les balises markdown si présentes
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        learning_block = json.loads(text)
        
        return learning_block
    
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur de parsing JSON: {str(e)}. Réponse reçue: {response.text[:200]}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur de génération: {str(e)}"
        )

@app.post("/api/generate/upload")
async def generate_from_upload(
    file: UploadFile = File(...),
    sujet: str = "",
    niveau: str = "Intermédiaire",
    objectif: str = "Apprentissage"
):
    """
    Génération basée sur documents uploadés (RAG)
    
    Cette route:
    1. Lit le document uploadé
    2. Extrait le texte
    3. Génère un bloc d'apprentissage basé sur ce contenu
    
    Args:
        file: Document (PDF, DOCX, TXT)
        sujet: Sujet spécifique à extraire
        niveau: Niveau de l'étudiant
        objectif: Objectif d'apprentissage
    
    Returns:
        LearningBlock: Bloc généré depuis le document
    """
    if not model:
        raise HTTPException(
            status_code=500, 
            detail="Clé API Gemini non configurée"
        )
    
    try:
        # Lire le contenu du fichier
        content = await file.read()
        
        # Extraction de texte selon le type
        text = await extract_text_from_file(content, file.filename)
        
        if not text:
            raise HTTPException(
                status_code=400, 
                detail="Impossible d'extraire du texte du document"
            )
        
        # Génération avec contexte RAG
        prompt = f"""{SYSTEM_PROMPT}

Contexte extrait du document:
{text[:4000]}  # Limite à 4000 caractères

Sujet: {sujet if sujet else "Contenu principal du document"}
Niveau: {niveau}
Objectif: {objectif}

Génère un bloc d'apprentissage basé sur CE document en JSON.
"""
        
        response = model.generate_content(prompt)
        
        # Extraire le JSON
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.startswith("```"):
            text_response = text_response[3:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
        
        text_response = text_response.strip()
        learning_block = json.loads(text_response)
        
        return learning_block
    
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur de parsing JSON: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors du traitement: {str(e)}"
        )

# Helper Functions
async def extract_text_from_file(content: bytes, filename: str) -> str:
    """
    Extrait le texte d'un fichier selon son type
    
    Args:
        content: Contenu binaire du fichier
        filename: Nom du fichier pour détecter l'extension
    
    Returns:
        str: Texte extrait
    """
    try:
        if filename.endswith('.pdf'):
            from PyPDF2 import PdfReader
            import io
            pdf = PdfReader(io.BytesIO(content))
            return "\n".join([page.extract_text() for page in pdf.pages])
        
        elif filename.endswith('.docx'):
            from docx import Document
            import io
            doc = Document(io.BytesIO(content))
            return "\n".join([para.text for para in doc.paragraphs])
        
        elif filename.endswith('.txt'):
            return content.decode('utf-8')
        
        else:
            # Tentative de décodage en texte brut
            return content.decode('utf-8')
    
    except Exception as e:
        raise HTTPException(
            status_code=400, 
            detail=f"Erreur d'extraction: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
