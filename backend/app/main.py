"""EduFlow AI - Backend API principale avec FastAPI

Ce fichier contient l'API backend pour EduFlow AI qui permet:
- Génération de blocs d'apprentissage via OpenAI GPT-4o
- Upload et traitement de documents (RAG)
- Création de quiz interactifs
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
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

# Client OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        "endpoints": ["/generate/direct", "/generate/upload", "/health"]
    }

@app.get("/health")
async def health_check():
    """Vérifier l'état de l'API"""
    return {"status": "healthy", "openai_key_configured": bool(os.getenv("OPENAI_API_KEY"))}

@app.post("/api/generate/direct")
async def generate_direct(request: GenerateDirectRequest):
    """
    Génération directe via GPT-4o sans documents externes
    
    Args:
        request: Contient sujet, niveau, objectif
    
    Returns:
        LearningBlock: Bloc d'apprentissage généré
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""
                Sujet: {request.sujet}
                Niveau: {request.niveau}
                Objectif: {request.objectif}
                
                Génère un bloc d'apprentissage complet en JSON.
                """}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        learning_block = json.loads(content)
        
        return learning_block
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de génération: {str(e)}")

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
    try:
        # Lire le contenu du fichier
        content = await file.read()
        
        # Extraction de texte selon le type
        text = await extract_text_from_file(content, file.filename)
        
        if not text:
            raise HTTPException(status_code=400, detail="Impossible d'extraire du texte du document")
        
        # Génération avec contexte RAG
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"""
                Contexte extrait du document:
                {text[:4000]}  # Limite à 4000 caractères
                
                Sujet: {sujet if sujet else "Contenu principal du document"}
                Niveau: {niveau}
                Objectif: {objectif}
                
                Génère un bloc d'apprentissage basé sur CE document.
                """}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        learning_block = json.loads(content)
        
        return learning_block
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")

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
        raise HTTPException(status_code=400, detail=f"Erreur d'extraction: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
