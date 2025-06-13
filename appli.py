import streamlit as st
import fitz  # PyMuPDF
import io

st.set_page_config(page_title="Éditeur PDF simple", layout="centered")
st.title("Éditeur PDF : Relevé de compte Trade Republic")
st.write("""
1. Importez un Relevé de compte Trade Republic.
2. Le contenu en dehors de la section **TRANSACTIONS** sera automatiquement supprimé.
3. **Téléchargez le PDF modifié.**
""")

uploaded_file = st.file_uploader("Choisissez un fichier PDF à modifier", type=["pdf"])

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    st.divider()

    with st.spinner("Traitement du PDF en cours..."):
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
        page.add_redact_annot(fitz.Rect(0, 0, page.rect.width, start_rect.y0), fill=(1, 1, 1))
        if start_idx == end_idx:
            page.add_redact_annot(fitz.Rect(0, end_rect.y0, page.rect.width, page.rect.height), fill=(1, 1, 1))
            page.apply_redactions()
        else:
            page.apply_redactions()
            page2 = doc[end_idx]
            page2.add_redact_annot(fitz.Rect(0, end_rect.y0, page2.rect.width, page2.rect.height), fill=(1, 1, 1))
            page2.apply_redactions()

        for j in range(doc.page_count - 1, -1, -1):
            if j < start_idx or j > end_idx:
                doc.delete_page(j)

        output_buffer = io.BytesIO()
        doc.save(output_buffer, garbage=4, deflate=True)
        st.success("PDF modifié avec succès !")
        st.download_button(
            label="📥 Télécharger le PDF modifié",
            data=output_buffer.getvalue(),
            file_name="document_modifie.pdf",
            mime="application/pdf"
        )
