import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Éditeur PDF simple", layout="centered")
st.title("📝 Éditeur PDF : modification du texte & suppression d'images")
st.write("""
1. Importez un fichier PDF avec texte sélectionnable.
2. Supprimez toutes les images (optionnel).
3. **Nouvelle option : ne conserver que le contenu entre les mots « TRANSACTIONS » et « APERÇU DU SOLDE ».**
4. Téléchargez le PDF modifié.
""")

uploaded_file = st.file_uploader("Choisissez un fichier PDF à modifier", type=["pdf"])

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    st.divider()

    # Suppression des images
    st.subheader("Suppression des images")
    remove_img = st.checkbox("Supprimer toutes les images du PDF", value=False)

    # Option section TRANSACTIONS -> APERÇU DU SOLDE
    keep_transactions = st.checkbox(
        "Conserver uniquement le contenu entre 'TRANSACTIONS' et 'APERÇU DU SOLDE'",
        value=False,
    )

    # Traitement du PDF
    if remove_img or keep_transactions:
        with st.spinner("Traitement du PDF en cours..."):
            # Ne conserver que la section Transactions
            if keep_transactions:
                start_idx = end_idx = None
                start_rect = end_rect = None
                # Recherche des pages et positions
                for i, p in enumerate(doc):
                    if start_idx is None:
                        s = p.search_for("TRANSACTIONS")
                        if s:
                            start_idx = i
                            start_rect = s[0]
                    if start_idx is not None and end_idx is None:
                        e = p.search_for("APERÇU DU SOLDE")
                        if e:
                            end_idx = i
                            end_rect = e[0]
                            break
                if start_idx is None or end_idx is None:
                    st.error("Mots clés introuvables dans le document.")
                    st.stop()
                # Redaction des zones hors section
                page = doc[start_idx]
                # Supprimer tout avant "TRANSACTIONS"
                page.add_redact_annot(fitz.Rect(0, 0, page.rect.width, start_rect.y0), fill=(1, 1, 1))
                if start_idx == end_idx:
                    # Supprimer la zone contenant "APERÇU DU SOLDE" ET tout ce qui suit
                    page.add_redact_annot(fitz.Rect(0, end_rect.y0, page.rect.width, page.rect.height), fill=(1, 1, 1))
                    page.apply_redactions()
                else:
                    page.apply_redactions()
                    page2 = doc[end_idx]
                    # Supprimer la zone contenant "APERÇU DU SOLDE" ET tout ce qui suit
                    page2.add_redact_annot(fitz.Rect(0, end_rect.y0, page2.rect.width, page2.rect.height), fill=(1, 1, 1))
                    page2.apply_redactions()
                # Suppression des pages hors section
                for j in range(doc.page_count - 1, -1, -1):
                    if j < start_idx or j > end_idx:
                        doc.delete_page(j)

            for page in doc:
                # Suppression des images
                if remove_img:
                    img_list = page.get_images(full=True)
                    for img in img_list:
                        page.delete_image(img[0])

            # Sauvegarde du PDF modifié
            output_buffer = io.BytesIO()
            doc.save(output_buffer, garbage=4, deflate=True)
            st.success("PDF modifié avec succès !")
            st.download_button(
                label="📥 Télécharger le PDF modifié",
                data=output_buffer.getvalue(),
                file_name="document_modifie.pdf",
                mime="application/pdf"
            )
    else:
        st.info("Aucune modification appliquée. Cochez une option pour générer le PDF.")
