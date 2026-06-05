# 📑 MAPA DO PROBLEMA: Triagem Documental Inteligente (Discovery)

**Data da Análise:** 25 de Fevereiro de 2026  
**Analista:** IA Especialista em Discovery & Estratégia  
**Status:** Avaliação de Investimento Crítica

---

## 1. Contexto e Cenário Atual
O ecossistema administrativo e jurídico brasileiro vive um paradoxo: a mídia do documento foi digitalizada (PDF/Imagem), mas a **triagem cognitiva** permanece analógica. Em repartições públicas, cartórios e escritórios, o fluxo de documentos é interrompido por um gargalo humano que verifica conformidade básica (presença de assinaturas, validades e tipos documentais) antes que o especialista possa realizar a análise de mérito.

## 2. Quem é Afetado e Como
* **Advogados e Paralegais:** Desvio de função. Profissionais com alto custo de hora-técnica são alocados em tarefas de baixo valor agregado, reduzindo a margem de lucro dos escritórios.
* **Servidores Públicos e Tabeliães:** Sobrecarga cognitiva e operacional. O volume de entrada supera a capacidade de triagem, gerando filas de espera (*backlog*) antes mesmo do início do processo.
* **Cidadãos e Empresas:** Vítimas da morosidade sistêmica. Um erro de checklist na triagem inicial pode atrasar a liberação de créditos, registros ou direitos por semanas.

## 3. Evidências Objetivas do Problema
### Dados Quantitativos
* **Fato (Congestionamento):** O relatório **Justiça em Números 2024 (CNJ)** aponta um estoque de **83,8 milhões de processos pendentes**. A taxa de congestionamento na fase de conhecimento (onde a triagem inicial ocorre) é superior a **70%**.
* **Fato (Custo Brasil):** Dados da **CNI (2024)** estimam que o "Custo Brasil" consome cerca de **R$ 1,7 trilhão por ano**, sendo a burocracia documental um dos pilares desse custo.
* **Evidência (Produtividade):** O *Clio Legal Trends Report* indica que advogados gastam, em média, apenas **2.3 horas por dia** em tarefas faturáveis; o restante é consumido por administração e organização documental.
* **Fato (Erro Humano):** Estudos de ergonomia cognitiva indicam que a taxa de erro em tarefas repetitivas de conferência visual oscila entre **1% e 5%**, aumentando linearmente com o cansaço do revisor.

### Dados Qualitativos
* **Evidência:** Inexistência de padronização nacional para documentos básicos (ex: RGs emitidos por diferentes estados com layouts distintos), o que dificulta a automação simples e exige inteligência contextual.

## 4. Impactos Atuais
| Dimensão | Impacto Observado |
| :--- | :--- |
| **Operacional** | Modelo de escala linear: para aumentar o volume de análise, é necessário contratar mais pessoas. |
| **Financeiro** | Custo de oportunidade elevado (especialistas fazendo trabalho de estagiários). |
| **Estratégico** | Perda de agilidade competitiva; demora no *onboarding* de clientes em setores regulados. |
| **Social** | Atraso na prestação jurisdicional e na eficiência do serviço público. |

## 5. Consequências de NÃO Agir
1.  **Estrangulamento do Setor Público:** Com a digitalização crescente, o volume de documentos submetidos crescerá em ritmo superior à capacidade de contratação de novos servidores.
2.  **Obsolescência Competitiva:** Escritórios que não automatizarem a triagem terão custos operacionais superiores aos concorrentes que utilizam IA, tornando-os menos atraentes em contratos de volume.

## 6. Riscos de Investir na Resolução
* **Risco Técnico (Alucinação):** Modelos de IA podem confirmar a presença de dados inexistentes ou falhar em documentos de baixa qualidade (OCR falho).
* **Risco de Integração:** Muitos sistemas legados (PJe, e-SAJ) não possuem APIs amigáveis, dificultando o fluxo automático de dados.
* **Risco de Compliance (LGPD):** O tratamento de dados pessoais sensíveis exige infraestrutura de segurança de alta complexidade e custo elevado.

## 7. Lacunas de Conhecimento Existentes
* Não há dados públicos exatos sobre o custo financeiro direto de *um erro* de checklist em cartórios (o custo é mitigado por seguros ou responsabilidade civil, mas não é transparente).
* Limitação na comprovação da eficácia da IA em documentos manuscritos extremamente antigos ou degradados.

## 8. Hipóteses Iniciais (A serem testadas)
* **H1:** A automação da triagem reduz o tempo total de resposta de um dossiê em pelo menos **65%**.
* **H2:** O custo de processamento via IA por documento é **80% menor** que o custo da hora-homem equivalente.
* **H3:** Usuários aceitarão a triagem automatizada se houver uma interface de "explicabilidade" (mostrando onde a IA encontrou cada dado).

## 9. Avaliação Crítica
O problema é **REAL** e **DIGNO DE INVESTIMENTO**. A dor é validada por indicadores macroeconômicos (Custo Brasil) e microeconômicos (produtividade jurídica). A solução não tenta substituir o especialista, mas sim limpar o ruído operacional, o que reduz a barreira de adoção cultural. O investimento em experimentos é o caminho racional, dado que a tecnologia de LLMs e Visão Computacional atual já supera a acurácia humana em tarefas de tédio prolongado.

---

### **PARECER FINAL: GO (PROSSEGUIR PARA EXPERIMENTOS)**

O problema possui relevância econômica e viabilidade técnica inicial comprovada por benchmarks de mercado. Recomenda-se o avanço para a fase de Prova de Conceito (PoC).

#### **O que precisa ser medido/comprovado agora:**
1.  **Acurácia Técnica:** Testar o checklist em um lote de 100 documentos "sujos" (baixa resolução) para definir a margem de erro real da IA.
2.  **Mapeamento de APIs:** Verificar a viabilidade de integração com o sistema alvo (ex: um ERP jurídico específico ou portal do tribunal).
3.  **Willingness to Pay:** Confirmar com 10 potenciais clientes o valor máximo por documento processado que manteria a solução lucrativa para eles.