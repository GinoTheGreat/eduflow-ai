# 🎓 EduFlow AI

> **Moteur d'apprentissage adaptatif propulsé par l'IA** - Génération de blocs pédagogiques intelligents avec OpenAI GPT-4o & Google Gemini

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991.svg)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Vue d'ensemble

**EduFlow AI** est une plateforme d'apprentissage adaptée qui transforme des notions complexes en micro-blocs pédagogiques structurés. L'application utilise l'IA générative pour créer:

✅ **Blocs de connaissance** personnalisés selon le niveau (Débutant/Intermédiaire/Avancé)  
✅ **Quiz interactifs** QCM avec explications détaillées  
✅ **Daily 5** - Rappels quotidiens pour consolidation mémorielle  
✅ **RAG (Retrieval-Augmented Generation)** - Upload de documents (PDF, DOCX, TXT)  

### 💡 Cas d'usage

- 🏫 **Étudiants en ingénierie/sciences** : Préparation d'examens, révisions ciblées
- 📚 **Apprentissage autonome** : Vulgarisation de concepts avancés
- 📝 **Formation continue** : Micro-learning adapté à votre rythme

---

## 🚀 Fonctionnalités clés

### 1️⃣ **Génération via API IA**
```
Utilisateur entre un sujet → GPT-4o/Gemini génère le contenu structuré
```

**Exemple de sortie JSON:**
```json
{
  "titre_du_bloc": "Transformée de Laplace",
  "resume_conceptuel": "La transformée de Laplace convertit une fonction du temps en fonction complexe...",
  "formules_cles": ["L{f(t)} = \\int_0^{\\infty} e^{-st} f(t) dt"],
  "analogie": "Comme traduire un livre d'une langue à une autre pour faciliter la compréhension",
  "daily_5": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"],
  "quiz": [...]
}
```

### 2️⃣ **Upload de Documents (RAG)**
```
Utilisateur upload PDF/DOCX → Extraction de texte → Génération contextualisée
```

**Formats supportés:**
- 📝 PDF (.pdf)
- 📄 Word (.docx)
- 📃 Texte (.txt)

### 3️⃣ **Rappels quotidiens automatiques**
- Notifications push via Firebase Cloud Messaging
- Scheduler APScheduler pour envoi à 9h chaque jour
- "Daily 5" points essentiels pour ancrage mémoriel

---

## 🛠️ Architecture technique

### Stack

#### Backend
```
🐍 Python 3.11+ avec FastAPI
🤖 OpenAI GPT-4o (principal)
🌟 Google Gemini (fallback optionnel)
📂 PostgreSQL + SQLAlchemy
📚 Pinecone (Vector Database pour RAG)
🔔 Firebase Admin SDK (notifications)
```

#### Frontend (prévu)
```
⚛️ React.js + TypeScript
🎨 Tailwind CSS
📦 Axios pour API calls
```

### Architecture RAG (Retrieval-Augmented Generation)

```
1. Upload Document (PDF/DOCX/TXT)
   ↓
2. Extraction de texte (PyPDF2, python-docx)
   ↓
3. Chunking + Embeddings (OpenAI Embeddings)
   ↓
4. Stockage dans Pinecone Vector DB
   ↓
5. Retrieval des chunks pertinents
   ↓
6. Génération LLM avec contexte augmenté
```

---

## 💻 Installation

### Prérequis
- Python 3.11+
- Clé API OpenAI ([Get one here](https://platform.openai.com/api-keys))
- (Optionnel) Compte Pinecone pour RAG avancé
- (Optionnel) Firebase pour notifications

### Étape 1: Cloner le repository
```bash
git clone https://github.com/GinoTheGreat/eduflow-ai.git
cd eduflow-ai
```

### Étape 2: Configuration Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Étape 3: Variables d'environnement

Créer un fichier `.env` dans `/backend` :

```env
# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxx

# Google Gemini (optionnel)
GEMINI_API_KEY=your_gemini_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/eduflow

# Pinecone (pour RAG avancé)
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-east-1-aws

# Firebase (pour notifications)
FIREBASE_CREDENTIALS=path/to/serviceAccountKey.json
```

### Étape 4: Lancer l'API

```bash
cd backend/app
python main.py
```

L'API sera accessible sur `http://localhost:8000`

📖 **Documentation interactive**: `http://localhost:8000/docs`

---

## 📡 Endpoints API

### 1. Génération directe

```http
POST /api/generate/direct
Content-Type: application/json

{
  "sujet": "Transformée de Laplace",
  "niveau": "Intermédiaire",
  "objectif": "Examen final"
}
```

**Réponse:**
```json
{
  "titre_du_bloc": "...",
  "resume_conceptuel": "...",
  "formules_cles": [...],
  "analogie": "...",
  "daily_5": [...],
  "quiz": [...]
}
```

### 2. Upload de document (RAG)

```http
POST /api/generate/upload
Content-Type: multipart/form-data

file: [fichier.pdf]
sujet: "Circuits RLC"
niveau: "Avancé"
objectif: "Application pratique"
```

### 3. Health Check

```http
GET /health
```

---

## 📚 Exemple d'utilisation

### Python Client

```python
import requests

url = "http://localhost:8000/api/generate/direct"

payload = {
    "sujet": "Optimisation linéaire",
    "niveau": "Intermédiaire",
    "objectif": "Projet pratique"
}

response = requests.post(url, json=payload)
block = response.json()

print(f"Titre: {block['titre_du_bloc']}")
print(f"Résumé: {block['resume_conceptuel']}")
print(f"\nDaily 5:")
for i, point in enumerate(block['daily_5'], 1):
    print(f"  {i}. {point}")
```

### cURL

```bash
curl -X POST "http://localhost:8000/api/generate/direct" \
  -H "Content-Type: application/json" \
  -d '{
    "sujet": "Théorème de Thévenin",
    "niveau": "Débutant",
    "objectif": "Examen final"
  }'
```

---

## 📊 Roadmap

- [x] Backend FastAPI avec OpenAI GPT-4o
- [x] Système RAG pour documents
- [x] Génération de quiz interactifs
- [ ] Frontend React.js avec interface utilisateur
- [ ] Système d'authentification (JWT)
- [ ] Notifications push quotidiennes
- [ ] Modèle de répétition espacée (Spaced Repetition)
- [ ] Export de blocs en PDF/Markdown
- [ ] Intégration Google Gemini
- [ ] Application mobile (React Native)

---

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Fork le projet
2. Crée ta branche (`git checkout -b feature/AmazingFeature`)
3. Commit tes changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvre une Pull Request

---

## 📝 License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 💬 Contact

**Gino TheGreat** - [@GinoTheGreat](https://github.com/GinoTheGreat)

Lien du projet: [https://github.com/GinoTheGreat/eduflow-ai](https://github.com/GinoTheGreat/eduflow-ai)

---

## ⭐ Star History

Si ce projet t'aide, n'hésite pas à donner une étoile ⭐!

---

*Built with ❤️ for students by students*
