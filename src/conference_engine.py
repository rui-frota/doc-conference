# pyrefly: ignore [missing-import]
from openai import OpenAI
import json
import re
import difflib
from collections import Counter

from config import API_BASE_URL, API_KEY, MODEL_ID

# Initialize OpenAI client with custom base URL
client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL
)

def normalize_text(text: str) -> str:
    """
    Normaliza um texto removendo acentos, pontuação e espaços extras para comparação.
    
    Args:
        text: Texto a ser normalizado.
        
    Returns:
        str: Texto normalizado.
    """
    # Converter para minúsculas
    text = text.lower()
    
    # Remover acentos usando unicodedata
    import unicodedata
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(char for char in text if not unicodedata.combining(char))
    
    # Remover pontuação e caracteres especiais, mantendo apenas letras, números e espaços
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    
    # Remover espaços extras
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def extract_keywords(text: str) -> set:
    """
    Extrai palavras-chave de um texto, removendo stopwords em português.
    
    Args:
        text: Texto de onde extrair as palavras-chave.
        
    Returns:
        set: Conjunto de palavras-chave.
    """
    stopwords_pt = {
        'de', 'do', 'da', 'dos', 'das', 'em', 'no', 'na', 'nos', 'nas', 
        'para', 'por', 'com', 'sem', 'que', 'e', 'ou', 'se', 'ma', 'ão', 
        'esta', 'esse', 'esta', 'esse', 'essa', 'isto', 'aquilo', 'ser', 
        'ter', 'sua', 'seu', 'suas', 'seus', 'o', 'a', 'os', 'as', 'um', 
        'uma', 'uns', 'umas', 'etc', 'art', 'doc', 'pd', 'resp', 'conforme'
    }
    
    normalized = normalize_text(text)
    words = normalized.split()
    
    # Filrar stopwords e palavras muito curtas
    keywords = set()
    for word in words:
        if word not in stopwords_pt and len(word) > 2:
            keywords.add(word)
    
    return keywords


def match_document_names(needed: str, uploaded: str) -> float:
    """
    Calcula um score de correspondência entre dois nomes de documentos.
    Retorna um score de 0.0 a 1.0.
    
    Estratégias de matching:
    1. Normalização e comparação direta
    2. Fuzzy matching com SequenceMatcher
    3. Similaridade Jaccard de palavras-chave
    
    Args:
        needed: Nome do documento necessário (do checklist).
        uploaded: Nome do arquivo enviado.
        
    Returns:
        float: Score de correspondência (0.0 a 1.0).
    """
    # Normalizar ambos os textos
    norm_needed = normalize_text(needed)
    norm_uploaded = normalize_text(uploaded)
    
    if norm_needed == norm_uploaded:
        return 1.0
    
    # Extrair palavras-chave
    keywords_needed = extract_keywords(needed)
    keywords_uploaded = extract_keywords(uploaded)
    
    if not keywords_needed or not keywords_uploaded:
        # Fallback para fuzzy matching se não houver keywords
        return difflib.SequenceMatcher(None, norm_needed, norm_uploaded).ratio()
    
    # Estratégia 1: Matching de palavras-chave (Jaccard similarity)
    intersection = keywords_needed & keywords_uploaded
    union = keywords_needed | keywords_uploaded
    jaccard_score = len(intersection) / len(union) if union else 0
    
    # Estratégia 2: Substring matching com palavras-chave
    keyword_match_score = 0.0
    if keywords_needed:
        matched_keywords = 0
        for kw in keywords_needed:
            if kw in norm_uploaded or norm_needed in norm_uploaded:
                matched_keywords += 1
        keyword_match_score = matched_keywords / len(keywords_needed)
    
    # Estratégia 3: Fuzzy matching do nome completo
    fuzzy_score = difflib.SequenceMatcher(None, norm_needed, norm_uploaded).ratio()
    
    # Verificar se as palavras-chave principais estão contidas
    substring_score = 0.0
    if norm_needed and norm_uploaded:
        # Verificar se o nome necessário está contido no nome enviado ou vice-versa
        if norm_needed in norm_uploaded or norm_uploaded in norm_needed:
            substring_score = 1.0
        else:
            # Verificar se a maioria das palavras do nome necessário aparece no enviado
            needed_words = norm_needed.split()
            uploaded_words = norm_uploaded.split()
            matched_words = sum(1 for w in needed_words if w in uploaded_words)
            substring_score = matched_words / len(needed_words) if needed_words else 0
    
    # Score combinado com pesos
    # Substring matching é o mais forte, seguido por keyword matching, depois fuzzy
    combined_score = (
        substring_score * 0.40 +
        jaccard_score * 0.25 +
        keyword_match_score * 0.20 +
        fuzzy_score * 0.15
    )
    
    return min(combined_score, 1.0)


def find_best_matches(required_documents: list[str], uploaded_filenames: list[str], threshold: float = 0.5) -> dict:
    """
    Encontra as melhores correspondências entre documentos necessários e arquivos enviados.
    
    Args:
        required_documents: Lista de documentos necessários.
        uploaded_filenames: Lista de nomes de arquivos enviados.
        threshold: Score mínimo para considerar uma correspondência (0.0 a 1.0).
        
    Returns:
        dict: Dicionário com:
            - "matches": {doc_necessario: (arquivo_correspondente, score)}
            - "missing": documentos necessários sem correspondência
            - "unmatched": arquivos enviados sem correspondência
    """
    matches = {}
    matched_required = set()
    matched_uploaded = set()
    
    # Calcular todos os scores de matching
    all_scores = []
    for req_doc in required_documents:
        for uploaded_file in uploaded_filenames:
            score = match_document_names(req_doc, uploaded_file)
            all_scores.append((req_doc, uploaded_file, score))
    
    # Ordenar por score descending
    all_scores.sort(key=lambda x: x[2], reverse=True)
    
    # Atribuir melhores matches primeiro (algoritmo guloso)
    for req_doc, uploaded_file, score in all_scores:
        if score >= threshold and req_doc not in matched_required and uploaded_file not in matched_uploaded:
            matches[req_doc] = (uploaded_file, score)
            matched_required.add(req_doc)
            matched_uploaded.add(uploaded_file)
    
    # Documentos necessários sem correspondência
    missing = [doc for doc in required_documents if doc not in matched_required]
    
    # Arquivos enviados sem correspondência
    unmatched = [f for f in uploaded_filenames if f not in matched_uploaded]
    
    return {
        "matches": matches,
        "missing": missing,
        "unmatched": unmatched
    }


def validate_document(text: str, checklist: list[str]) -> dict:
    """
    Avalia o texto do documento contra a lista de verificação fornecida usando OpenAI Compatible API.
    """
    if not text.strip():
        return {"error": "Nenhum texto para avaliar."}
        
    prompt = f"""
    Você é um analista de documentos altamente preciso. Avalie o seguinte texto do documento contra a lista de verificação fornecida.
    Para cada item da lista de verificação, determine se o documento satisfaz o requisito com base APENAS no texto fornecido.
    
    Lista de Verificação:
    {json.dumps(checklist, indent=2)}
    
    Texto do Documento:
    '''
    {text}
    '''
    
    Forneça sua avaliação em formato JSON estrito. O JSON deve ser uma lista de objetos, onde cada objeto tem exatamente estas chaves:
    - "item": a string exata do item da lista de verificação
    - "status": exatamente um dos valores: "Aprovado", "Rejeitado" ou "Revisão"
    - "reason": Uma breve explicação do porquê este status foi dado com base no texto.
    
    Responda APENAS com o array JSON bruto. Não inclua blocos de markdown como json ou qualquer outra introdução ou conclusão.
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Removes markdown code blocks if present
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
            
        return json.loads(result_text)
    except Exception as e:
        error_msg = f"Falha ao validar documento com a API OpenAI Compatible: {str(e)}"
        return {"error": error_msg}


def cross_reference_documents(required_documents: list[str], uploaded_docs: dict[str, str], name_threshold: float = 0.5) -> dict:
    """
    Cruza os documentos necessários do checklist com os documentos anexados pelo usuário.
    Usa matching inteligente por nome E classificação por IA para resultados mais precisos.
    
    Args:
        required_documents: Lista de documentos necessários extraída do checklist.
        uploaded_docs: Dicionário com nome do arquivo como chave e texto extraído como valor.
        name_threshold: Threshold para matching por nome de arquivo (0.0 a 1.0).
        
    Returns:
        dict: Um dicionário com os resultados do cruzamento contendo:
            - "found": {doc_necessario: texto_do_documento, ...}
            - "missing": lista de documentos faltando
            - "classification": {filename: doc_classified, ...}
            - "unclassified": lista de arquivos não classificados
            - "name_matches": {doc_necessario: (filename, score)} matches por nome
            - "matched_files": lista de arquivos já identificados por nome
    """
    # Initialize result structure
    result = {
        "found": {},
        "missing": [],
        "classification": {},
        "unclassified": [],
        "name_matches": {},
        "matched_files": set()
    }
    
    # If no required documents, return early
    if not required_documents:
        result["missing"] = []
        result["warning"] = "Nenhum documento necessário foi identificado no checklist."
        return result
    
    # If no uploaded documents, all are missing
    if not uploaded_docs:
        result["missing"] = list(required_documents)
        return result
    
    # === Etapa 1: Tentar matching por nome de arquivo primeiro (mais rápido, sem API call) ===
    uploaded_filenames = list(uploaded_docs.keys())
    name_matches = find_best_matches(required_documents, uploaded_filenames, threshold=name_threshold)
    
    # Processar matches por nome
    for req_doc, (filename, score) in name_matches["matches"].items():
        result["found"][req_doc] = uploaded_docs[filename]
        result["classification"][filename] = req_doc
        result["name_matches"][req_doc] = (filename, score)
        result["matched_files"].add(filename)
    
    # Adicionar documentos faltantes (sem match por nome)
    result["missing"] = list(name_matches["missing"])
    
    # === Etapa 2: Para arquivos não matching por nome, usar IA para classificar ===
    for filename, text in uploaded_docs.items():
        # Pular arquivos já matching por nome
        if filename in result["matched_files"]:
            continue
        
        if not text.strip():
            result["unclassified"].append(filename)
            continue
        
        # Extract just the document name from the path
        doc_name = filename.split('/')[-1] if '/' in filename else filename
        doc_name = doc_name.rsplit('.', 1)[0] if '.' in doc_name else doc_name
        
        # Apenas documentos que ainda não foram encontrados precisam de classificação por IA
        docs_needing_ai = result["missing"] if result["missing"] else [filename]
        
        classify_client = OpenAI(
            api_key=API_KEY,
            base_url=API_BASE_URL
        )
        
        prompt = f"""
        Você é um analista de documentos. Sua tarefa é classificar o documento abaixo em um dos tipos disponíveis.
        
        Tipos disponíveis: {', '.join(docs_needing_ai)}
        
        Documento a classificar (nome do arquivo): {doc_name}
        
        Conteúdo do documento:
        '''
        {text[:4000]}
        '''
        
        Responda APENAS com o nome exato de um dos tipos disponíveis. Se não conseguir classificar, responda "Não classificado". Sem explicações.
        """
        
        try:
            response = classify_client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            classified_type = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if "```" in classified_type:
                classified_type = classified_type.split("```")[1].strip()
            
            # Check if the classified type matches any required document
            matched = False
            for req_doc in required_documents:
                if req_doc.lower() in classified_type.lower() or classified_type.lower() in req_doc.lower():
                    result["found"][req_doc] = uploaded_docs[filename]
                    result["classification"][filename] = req_doc
                    matched = True
                    break
            if not matched:
                result["unclassified"].append(filename)

        except Exception as e:
            result["unclassified"].append(filename)

    # Convert matched_files set to list for JSON serialization
    result["matched_files"] = list(result["matched_files"])
    
    return result


def validate_with_cross_reference(required_documents: list[str], uploaded_docs: dict[str, str], threshold: float = 0.5) -> list:
    """
    Valida documentos cruzando o checklist com os documentos enviados.
    Esta é a função principal que orquestra o matching, classificação e validação.
    
    Args:
        required_documents: Lista de documentos necessários do checklist.
        uploaded_docs: Dicionário com filename -> texto_extraido.
        threshold: Threshold para matching por nome.
        
    Returns:
        list: Lista de resultados de validação.
    """
    # Step 1: Cross-reference to find matches
    cross_ref = cross_reference_documents(required_documents, uploaded_docs, name_threshold=threshold)
    
    # Build the result
    results = []
    
    # Add results for found documents
    for req_doc, text in cross_ref["found"].items():
        # Validate the found document content
        doc_results = validate_document(text, [req_doc])
        if isinstance(doc_results, list):
            for item in doc_results:
                item["document"] = req_doc
                item["status"] = "Encontrado"
                results.append(item)
    
    # Add results for missing documents
    for missing_doc in cross_ref["missing"]:
        results.append({
            "item": missing_doc,
            "status": "Faltando",
            "reason": f"O documento '{missing_doc}' não foi encontrado nos arquivos anexados.",
            "document": missing_doc
        })
    
    # Add results for unclassified documents
    for unclass_doc in cross_ref["unclassified"]:
        results.append({
            "item": unclass_doc,
            "status": "Não classificado",
            "reason": f"O documento '{unclass_doc}' não pôde ser classificado automaticamente.",
            "document": unclass_doc
        })
    
    return results
