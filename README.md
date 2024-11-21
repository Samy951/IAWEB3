# RAG Chatbot avec Ollama et Google Drive

Ce projet implémente un chatbot utilisant la technique RAG (Retrieval Augmented Generation) pour répondre à des questions en se basant sur des documents PDF stockés dans Google Drive.

## Fonctionnalités

- **Mode RAG vs Non-RAG** : Possibilité de comparer les réponses avec et sans contexte documentaire
- **Température ajustable** : Contrôle de la créativité des réponses
- **Intégration Google Drive** : Lecture automatique des PDFs depuis un dossier Drive
- **Interface utilisateur** : Interface web intuitive avec Streamlit
- **Persistance des embeddings** : Stockage local des embeddings pour de meilleures performances

## Architecture

- **LLM** : Ollama (llama2) pour la génération de texte
- **Stockage** : Google Drive pour les documents sources
- **Vectorisation** : ChromaDB pour le stockage des embeddings
- **Interface** : Streamlit pour l'interface utilisateur

## Prérequis

- Python 3.8+
- Ollama installé localement
- Un compte Google avec accès à l'API Drive
- Les documents PDF à analyser dans un dossier Google Drive

## Installation

1. **Cloner le repository**
