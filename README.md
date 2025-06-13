# streamlit_pdf_editeur

Cette application Streamlit permet de modifier un fichier PDF directement dans le navigateur. Les fonctionnalités proposées sont :

- Remplacement de texte par recherche exacte.
- Suppression de toutes les images d'un document.
- **Extraction automatique du contenu compris entre les mots "TRANSACTIONS" et "APERÇU DU SOLDE".** Tout le reste (texte et images) est supprimé.
- Téléchargement du PDF obtenu après traitement.

Installez les dépendances avec :
```
pip install -r requirements.txt
```
