# pyrefly: ignore [missing-import]
import pdfplumber
# pyrefly: ignore [missing-import]
from openai import OpenAI
import json
from config import API_BASE_URL, API_KEY, MODEL_ID

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extrai texto de um arquivo PDF fornecido.
    
    Args:
        pdf_file: Um objeto tipo arquivo contendo os dados do PDF (e.g., do file_uploader do Streamlit).
        
    Returns:
        str: O texto extraído de todas as páginas do PDF.
    """
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text


def parse_checklist(checklist_text: str) -> list[str]:
    """
    Usa IA para extrair apenas os nomes dos documentos solicitados em um checklist.
    Ignora descrições, instruções e texto descritivo de cada item.
    
    Args:
        checklist_text: O texto extraído do PDF do checklist.
        
    Returns:
        list[str]: Uma lista limpa com os nomes dos documentos necessários.
    """
    # Limitar o texto para evitar sobrecarga no modelo
    checklist_truncated = checklist_text[:3000]
    
    client = OpenAI(
        api_key=API_KEY,
        base_url=API_BASE_URL,
        timeout=60.0  # timeout de 60 segundos
    )
    
    prompt = f"""Extraia APENAS os nomes dos documentos solicitados neste checklist. Retorne um array JSON de strings. Exemplo: ["RG", "CPF", "Comprovante de Residência"]

Checklist:
{checklist_truncated}

Responda APENAS com o array JSON. Sem explicações."""
    
    try:
        print(f"[DEBUG] parse_checklist chamando modelo {MODEL_ID}...")
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Debug: print raw response
        print(f"[DEBUG] parse_checklist resposta: {result_text[:300]}")
        
        # Remove markdown code blocks if present
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        documents = json.loads(result_text)
        
        # Validate that we got a list of strings
        if isinstance(documents, list) and all(isinstance(doc, str) for doc in documents):
            print(f"[DEBUG] parse_checklist extraiu {len(documents)} documentos via IA")
            for i, d in enumerate(documents):
                print(f"  {i+1}. {d}")
            return documents
        else:
            print("[DEBUG] parse_checklist IA retornou formato inválido, usando fallback")
            return _fallback_extract(checklist_text)
    except Exception as e:
        print(f"[DEBUG] parse_checklist erro: {e}, usando fallback")
        return _fallback_extract(checklist_text)


def _fallback_extract(text: str) -> list[str]:
    """
    Fallback extraction using pattern matching. Very aggressive to ensure we get documents.
    """
    import re
    
    documents = []
    lines = text.split('\n')
    
    # Pattern 1: Numbered/bulleted list items
    list_patterns = [
        r'^\s*\d+[\.\)]\s+(.+)$',          # "1. Texto" or "1) Texto"
        r'^\s*[IVX]+[\.\)]\s+(.+)$',        # "I. Texto" or "I) Texto"
        r'^\s*[a-z][\.\)]\s+(.+)$',         # "a. Texto" or "a) Texto"
        r'^\s*[\u2022\u2013\u2014\*]\s+(.+)$',  # "• Texto" or "- Texto"
        r'^\s*[\(]\d+[\)]\s+(.+)$',         # "(1) Texto"
    ]
    
    # Pattern 2: "DOCUMENTO: XYZ" or "TIPO: XYZ"
    doc_label_pattern = r'^\s*(?:DOCUMENTO|TIPO|ARQUIVO|ITEM|REQUISITO)\s*:\s+(.+)$'
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        if len(line_stripped) < 3:
            continue
        if len(line_stripped) > 80:
            continue
        
        # Check list patterns
        for pattern in list_patterns:
            match = re.match(pattern, line_stripped)
            if match:
                doc_name = match.group(1).strip()
                # Clean common noise
                doc_name = re.sub(r'^[-–—•]+$', '', doc_name).strip()
                if doc_name and len(doc_name.split()) <= 15:
                    if doc_name not in documents:
                        documents.append(doc_name)
                break
        
        # Check doc label pattern
        if not any(doc_name == line_stripped for doc_name in documents):
            label_match = re.match(doc_label_pattern, line_stripped, re.IGNORECASE)
            if label_match:
                doc_name = label_match.group(1).strip()
                if doc_name and len(doc_name.split()) <= 15:
                    if doc_name not in documents:
                        documents.append(doc_name)
    
    # If still got too many, cap it
    if len(documents) > 30:
        documents = documents[:30]
    
    return documents


def classify_document_with_ai(document_text: str, available_types: list[str]) -> str:
    """
    Usa IA para classificar um documento em um dos tipos disponíveis.
    
    Args:
        document_text: O texto extraído do documento a ser classificado.
        available_types: Lista de tipos de documentos disponíveis para classificação.
        
    Returns:
        str: O tipo de documento mais provável.
    """
    client = OpenAI(
        api_key=API_KEY,
        base_url=API_BASE_URL
    )
    
    prompt = f"""
    Você é um analista de documentos. Sua tarefa é classificar o documento abaixo em um dos tipos disponíveis.
    
    Tipos disponíveis: {', '.join(available_types)}
    
    Documento a classificar:
    '''
    {document_text[:4000]}
    '''
    
    Responda APENAS com o nome exato de um dos tipos disponíveis. Sem explicações, sem texto adicional.
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
        
        result = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if "```" in result:
            result = result.split("```")[1].strip()
        
        # Find the closest match in available types
        for doc_type in available_types:
            if doc_type.lower() in result.lower() or result.lower() in doc_type.lower():
                return doc_type
        
        # If no match found, return the raw result
        return result
    except Exception:
        # Fallback: return unknown
        return "Não classificado"