import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Éditeur PDF simple", layout="centered")
st.title("📝 Éditeur PDF : modification du texte & suppression d'images")
st.write("""
1. Importez un fichier PDF avec texte sélectionnable.
2. Remplacez un texte spécifique par un nouveau texte.
3. Supprimez toutes les images (optionnel).
4. **Nouvelle option : ne conserver que le contenu entre les mots « TRANSACTIONS » et « APERÇU DU SOLDE ».**
5. Téléchargez le PDF modifié.
""")

uploaded_file = st.file_uploader("Choisissez un fichier PDF à modifier", type=["pdf"])

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Aperçu du texte
    st.subheader("Aperçu du texte (par page)")
    tab_pages = st.tabs([f"Page {i+1}" for i in range(doc.page_count)])
    for i, page in enumerate(doc):
        with tab_pages[i]:
            text = page.get_text()
            st.text_area(f"Texte extrait (Page {i+1})", text, height=200, disabled=True)

    st.divider()
    # Remplacement de texte
    st.subheader("Remplacement de texte")
    col1, col2 = st.columns(2)
    with col1:
        old_text = st.text_input("Texte à remplacer (sensible à la casse)")
    with col2:
        new_text = st.text_input("Nouveau texte", value="")
    st.caption(
        "⚠️ Ne remplace que les occurrences exactes du texte sur toutes les pages. Limitez le remplacement à des mots/phrases courts."
    )
    replace_btn = st.button("Appliquer le remplacement")

    # Suppression des images
    st.subheader("Suppression des images")
    remove_img = st.checkbox("Supprimer toutes les images du PDF", value=False)

    # Option section TRANSACTIONS -> APERÇU DU SOLDE
    keep_transactions = st.checkbox(
        "Conserver uniquement le contenu entre 'TRANSACTIONS' et 'APERÇU DU SOLDE'",
        value=False,
    )

    # Traitement du PDF
    if replace_btn or remove_img or keep_transactions:
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
                # Redaction hors section
                page = doc[start_idx]
                # Supprimer tout avant "TRANSACTIONS"
                page.add_redact_annot(fitz.Rect(0, 0, page.rect.width, start_rect.y0), fill=(1, 1, 1))
                # Supprimer tout après "APERÇU DU SOLDE"
                if start_idx == end_idx:
                    page.add_redact_annot(fitz.Rect(0, end_rect.y1, page.rect.width, page.rect.height), fill=(1, 1, 1))
                    page.apply_redactions()
                else:
                    page.apply_redactions()
                    page2 = doc[end_idx]
                    page2.add_redact_annot(fitz.Rect(0, end_rect.y1, page2.rect.width, page2.rect.height), fill=(1, 1, 1))
                    page2.apply_redactions()
                # Suppression des pages hors section
                for j in range(doc.page_count - 1, -1, -1):
                    if j < start_idx or j > end_idx:
                        doc.delete_page(j)

            for page in doc:
                # Remplacement de texte
                if replace_btn and old_text.strip():
                    rects = page.search_for(old_text)
                    for rect in rects:
                        page.add_redact_annot(rect, new_text, fill=(1, 1, 1))
                    if rects:
                        page.apply_redactions()
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
        st.info("Aucune modification appliquée. Cochez une option ou lancez le remplacement pour générer le PDF.")

