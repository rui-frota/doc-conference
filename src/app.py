import streamlit as st
import os
from document_parser import extract_text_from_pdf, parse_checklist
from conference_engine import validate_with_cross_reference, validate_document, match_document_names, find_best_matches

st.set_page_config(page_title="Conferência de Documentos", layout="wide")

st.title("⚖️ Conferência de Documentos")
st.markdown("Anexe um checklist de documentos e todos os documentos necessários para validação automática via IA.")

# Initialize session state
if "checklist_loaded" not in st.session_state:
    st.session_state.checklist_loaded = False
if "required_documents" not in st.session_state:
    st.session_state.required_documents = []
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = {}  # {filename: text_content}
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []  # list of uploaded file objects
if "doc_name_threshold" not in st.session_state:
    st.session_state.doc_name_threshold = 0.5
if "filter_status" not in st.session_state:
    st.session_state.filter_status = "Todos"
if "filter_keyword" not in st.session_state:
    st.session_state.filter_keyword = ""

# ============================================================
# SIDEBAR: Checklist Upload
# ============================================================
st.sidebar.header("📋 Lista de Verificação")
checklist_file = st.sidebar.file_uploader("Upload do Checklist (PDF)", type=["pdf"], key="sidebar_checklist")

if checklist_file is not None:
    with st.spinner("Extraindo documentos necessários do checklist..."):
        try:
            checklist_text = extract_text_from_pdf(checklist_file)
            required_docs = parse_checklist(checklist_text)
            
            st.session_state.required_documents = required_docs
            st.session_state.checklist_loaded = True
            st.sidebar.success("✅ Checklist processado com sucesso!")
            
            with st.sidebar.expander("📄 Documentos Necessários"):
                if required_docs:
                    for i, doc in enumerate(required_docs):
                        st.write(f"{i+1}. **{doc}**")
                    st.divider()
                    st.info(f"**Total:** {len(required_docs)} documento(s) necessário(s)")
                else:
                    st.warning("Nenhum documento necessário identificado.")
                    
            with st.sidebar.expander("📝 Texto Completo do Checklist"):
                st.text(checklist_text[:2000] + "..." if len(checklist_text) > 2000 else checklist_text)
                
        except Exception as e:
            st.sidebar.error(f"Erro ao processar checklist: {e}")
else:
    st.sidebar.info("Faça o upload de um checklist em PDF para começar.")

# ============================================================
# MAIN AREA: Document Upload Section
# ============================================================
st.header("📎 Anexo dos Documentos")

if st.session_state.checklist_loaded and st.session_state.required_documents:
    st.subheader(f"Documentos necessários: {len(st.session_state.required_documents)}")
    
    # Display required documents as tags/chips
    col_tags, col_upload = st.columns([3, 1])
    
    with col_tags:
        st.markdown("**Documentos exigidos:**")
        for doc in st.session_state.required_documents:
            st.markdown(f'📄 `{doc}`')
    
    with col_upload:
        # Multi-file uploader
        uploaded_files = st.file_uploader(
            "Anexe os documentos (PDF)", 
            type=["pdf"], 
            accept_multiple_files=True,
            key="doc_uploader",
            help="Selecione um ou mais documentos para anexar"
        )
        
        if uploaded_files:
            # Process new uploads
            new_docs = {}
            for uploaded_file in uploaded_files:
                with st.spinner(f"Processando {uploaded_file.name}..."):
                    try:
                        text = extract_text_from_pdf(uploaded_file)
                        new_docs[uploaded_file.name] = text
                        
                        # Add to session state
                        if uploaded_file.name not in st.session_state.uploaded_files:
                            st.session_state.uploaded_files.append(uploaded_file.name)
                            st.session_state.uploaded_docs[uploaded_file.name] = text
                    except Exception as e:
                        st.error(f"Erro ao processar {uploaded_file.name}: {e}")
            
            if new_docs:
                st.success(f"✅ {len(new_docs)} documento(s) anexado(s) com sucesso!")
    
    # Display uploaded documents status
    st.subheader("📊 Status dos Documentos")
    
    # Run robust matching to update session state
    uploaded_filenames = list(st.session_state.uploaded_docs.keys())
    if uploaded_filenames:
        # Use the robust matching function
        match_result = find_best_matches(
            st.session_state.required_documents,
            uploaded_filenames,
            threshold=st.session_state.doc_name_threshold
        )
        
        # Save match results to session state for filtering
        st.session_state.match_results = match_result
        
        # Get document statuses for filtering
        doc_statuses = {}
        for req_doc in st.session_state.required_documents:
            if req_doc in match_result["matches"]:
                doc_statuses[req_doc] = "Encontrado"
            else:
                doc_statuses[req_doc] = "Faltando"
        
        st.session_state.doc_statuses = doc_statuses
    else:
        st.session_state.doc_statuses = {doc: "Faltando" for doc in st.session_state.required_documents}
    
    # Apply filters
    filter_keyword = st.session_state.filter_keyword
    filter_status = st.session_state.filter_status
    
    filtered_docs = []
    for req_doc, status in st.session_state.doc_statuses.items():
        # Apply keyword filter
        if filter_keyword and filter_keyword.lower() not in req_doc.lower():
            continue
        
        # Apply status filter
        if filter_status != "Todos" and status != filter_status:
            continue
        
        filtered_docs.append((req_doc, status))
    
    # Update session state with filtered docs
    st.session_state.filtered_docs = filtered_docs
    
    # Display filter controls
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        st.session_state.filter_keyword = st.text_input("🔍 Filtrar por palavra-chave", value=st.session_state.filter_keyword, key="filter_keyword_input")
    with filter_col2:
        st.session_state.filter_status = st.selectbox("📊 Filtrar por status", ["Todos", "Encontrado", "Faltando"], key="filter_status_select")
    with filter_col3:
        new_threshold = st.slider("🎯 Threshold do matching", 0.0, 1.0, st.session_state.doc_name_threshold, 0.05, key="threshold_slider")
        if new_threshold != st.session_state.doc_name_threshold:
            st.session_state.doc_name_threshold = new_threshold
    
    # Display summary metrics
    found_count = sum(1 for _, s in st.session_state.doc_statuses.items() if s == "Encontrado")
    missing_count = sum(1 for _, s in st.session_state.doc_statuses.items() if s == "Faltando")
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"✅ Encontrados: {found_count}/{len(st.session_state.doc_statuses)}")
    with col2:
        st.warning(f"❌ Faltando: {missing_count}/{len(st.session_state.doc_statuses)}")
    
    # Display filtered results
    if filtered_docs:
        st.markdown("**Documentos filtrados:**")
        for req_doc, status in filtered_docs:
            col_a, col_b, col_c = st.columns([3, 1, 1])
            
            if status == "Encontrado":
                # Find the matched file
                matched_file = None
                matched_score = None
                for doc, (filename, score) in st.session_state.match_results.get("matches", {}).items():
                    if doc == req_doc:
                        matched_file = filename
                        matched_score = score
                        break
                
                with col_a:
                    st.success(f"✅ **{req_doc}**")
                    if matched_file and matched_score:
                        st.caption(f"📄 {matched_file} (score: {matched_score:.2f})")
                with col_b:
                    st.write(f"📄 **{matched_file.split('/')[-1]}**" if matched_file else "❌")
                with col_c:
                    # Show preview option
                    if matched_file:
                        if st.button("👁️", key=f"preview_doc_{req_doc}"):
                            st.session_state[f"show_preview_doc_{req_doc}"] = True
            else:
                with col_a:
                    st.warning(f"❌ **{req_doc}**")
                with col_b:
                    st.write("❓")
                with col_c:
                    st.info("N/A")
    else:
        st.info("Nenhum documento encontrado com os filtros aplicados.")
    
    # Preview expanders for found documents
    for req_doc in st.session_state.doc_statuses.keys():
        preview_key = f"show_preview_doc_{req_doc}"
        if st.session_state.get(preview_key, False):
            # Find the matched file
            matched_file = None
            for doc, (filename, score) in st.session_state.match_results.get("matches", {}).items():
                if doc == req_doc:
                    matched_file = filename
                    break
            
            if matched_file and matched_file in st.session_state.uploaded_docs:
                with st.expander(f"Preview: {req_doc} ({matched_file.split('/')[-1]})"):
                    doc_text = st.session_state.uploaded_docs[matched_file]
                    st.text(doc_text[:2000] + "..." if len(doc_text) > 2000 else doc_text)
                    if st.button("Fechar preview", key=f"close_preview_doc_{req_doc}"):
                        st.session_state[preview_key] = False
                        st.rerun()
    
    # Show uploaded files list with option to remove (only unmatched files)
    if st.session_state.uploaded_docs:
        with st.expander("📁 Documentos Anexados"):
            for filename in st.session_state.uploaded_docs.keys():
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.write(f"📄 **{filename}**")
                with col2:
                    if st.button(f"❌", key=f"remove_{filename}"):
                        st.session_state.uploaded_docs.pop(filename, None)
                        st.session_state.uploaded_files = [f for f in st.session_state.uploaded_files if f != filename]
                        st.rerun()
                with col3:
                    # Show preview option
                    if st.button("👁️", key=f"preview_{filename}"):
                        st.session_state[f"show_preview_{filename}"] = True
            
            # Preview expanders
            for filename in list(st.session_state.uploaded_docs.keys()):
                preview_key = f"show_preview_{filename}"
                if st.session_state.get(preview_key, False):
                    with st.expander(f"Preview: {filename}"):
                        st.text(st.session_state.uploaded_docs[filename][:1000] + "..." if len(st.session_state.uploaded_docs[filename]) > 1000 else st.session_state.uploaded_docs[filename])
                        if st.button("Fechar preview", key=f"close_{filename}"):
                            st.session_state[preview_key] = False
                            st.rerun()

# ============================================================
# ANALYSIS SECTION
# ============================================================
if st.session_state.checklist_loaded and st.session_state.required_documents and st.session_state.uploaded_docs:
    st.divider()
    st.header("🔍 Análise")
    
    col_btn, col_info = st.columns([1, 3])
    
    with col_btn:
        if st.button("🚀 Executar Análise de Cruzamento", type="primary", use_container_width=True):
            with st.spinner("Cruzando documentos e analisando..."):
                try:
                    results = validate_with_cross_reference(
                        st.session_state.required_documents,
                        st.session_state.uploaded_docs
                    )
                    
                    st.session_state.analysis_results = results
                    st.session_state.analysis_loaded = True
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro na análise: {e}")
    
    # Display results
    if st.session_state.get("analysis_loaded", False) and "analysis_results" in st.session_state:
        results = st.session_state.analysis_results
        
        # Summary
        found_count = sum(1 for r in results if r.get("status") in ["Encontrado", "Aprovado"])
        missing_count = sum(1 for r in results if r.get("status") == "Faltando")
        review_count = sum(1 for r in results if r.get("status") in ["Revisão", "Rejeitado"])
        unclassified_count = sum(1 for r in results if r.get("status") == "Não classificado")
        
        st.subheader("📊 Resumo da Análise")
        
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        with summary_col1:
            st.metric("✅ Encontrados", found_count)
        with summary_col2:
            st.metric("❌ Faltando", missing_count)
        with summary_col3:
            st.metric("⚠️ Revisão", review_count)
        with summary_col4:
            st.metric("❓ Não classificados", unclassified_count)
        
        st.divider()
        st.subheader("📋 Resultados Detalhados")
        
        for item in results:
            status = item.get("status", "")
            doc_name = item.get("document", item.get("item", "Desconhecido"))
            reason = item.get("reason", "")
            
            if status == "Encontrado":
                with st.expander(f"✅ **{doc_name}** - Encontrado", expanded=False):
                    st.write(f"**Motivo:** {reason}")
            elif status == "Aprovado":
                with st.expander(f"✅ **{doc_name}** - Aprovado", expanded=False):
                    st.write(f"**Motivo:** {reason}")
            elif status == "Rejeitado":
                with st.expander(f"❌ **{doc_name}** - Rejeitado", expanded=False):
                    st.write(f"**Motivo:** {reason}")
            elif status == "Faltando":
                st.error(f"❌ **{doc_name}** - {status}")
                st.error(f"*{reason}*")
            elif status == "Revisão":
                with st.expander(f"⚠️ **{doc_name}** - Revisão Necessária", expanded=False):
                    st.write(f"**Motivo:** {reason}")
            elif status == "Não classificado":
                st.warning(f"❓ **{doc_name}** - {status}")
                st.warning(f"*{reason}*")
            else:
                st.info(f"📄 **{doc_name}** - {status}")
                st.write(f"{reason}")

# ============================================================
# WELCOME SCREEN (no checklist loaded)
# ============================================================
if not st.session_state.checklist_loaded:
    st.divider()
    st.markdown("""
### Como usar:

1. **Upload do Checklist**: Na barra lateral, faça o upload de um checklist em PDF que contenha a lista de documentos necessários.

2. **Anexe os Documentos**: Após o checklist ser processado, use o botão "Anexe os documentos" para carregar todos os documentos PDF necessários.

3. **Executar Análise**: Clique em "Executar Análise de Cruzamento" para que a IA cruze os documentos anexados com o checklist e identifique:
   - ✅ Documentos encontrados e válidos
   - ❌ Documentos faltando
   - ⚠️ Documentos com problemas
   - ❓ Documentos não classificados
    """)