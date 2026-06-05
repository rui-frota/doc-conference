# Legal Document Conference POC (Discovery)

## Goal
To validate the technical and market feasibility of automating document conference in bureaucratic sectors, specifically focusing on the legal and public administration domains. This PoC aims to test hypotheses regarding efficiency gains, accuracy, and user acceptance.

## Tech Stack
*   **Language:** Python (planned for backend/scripting)
*   **AI/OCR:** [To be determined - likely Google Vision, AWS Textract, or open-source alternatives]
*   **Validation:** [To be determined - likely manual verification against ground truth]

## How to Run
1. Ensure you have Python 3 installed.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Ensure you have [Ollama](https://ollama.com/) installed and running locally, and pull the `llama3.2` model:
   ```bash
   ollama pull llama3.2
   ```
5. Run the Streamlit app:
   ```bash
   streamlit run src/app.py
   ```

---

## Discovery Analysis

### 1. Context and Current Scenario
Brazil has one of the most complex bureaucracies in the world. In the legal sector, the "Justiça em Números" (CNJ) report points out that the backlog of pending cases exceeds 80 million.
*   **Current Process:** Conference is predominantly manual, based on "eye-balling" against PDF or paper checklists.
*   **Volume:** Medium-sized offices deal with hundreds of petitions and attached documents daily.
*   **Digitization:** Although the process is electronic (PJe, e-SAJ), the analysis of file content remains analog (human).

### 2. Who is Affected and How
*   **Lawyers and Paralegals:** Role deviation. Qualified professionals spend up to 30% of their time on administrative/repetitive tasks.
*   **Public Servants:** Overload and procedural bottlenecks, resulting in delays in citizen service.
*   **Notaries:** Civil and administrative liability for conference errors in deeds and registrations.
*   **Companies (Compliance/HR):** Slowness in supplier and employee onboarding.

### 3. Objective Evidence of the Problem
*   **Quantitative Data:** Cognitive ergonomics studies indicate a human error rate in repetitive data entry/conference tasks between 1% and 4% under normal conditions, increasing drastically with fatigue.
*   **Qualitative Data:** The "Brazil Cost" related to bureaucracy consumes about R$ 2.6 trillion per year from companies (CNI data), where document conference is a central component of administrative overhead.
*   **Fact:** The diversity of document layouts (RG, CNH, Articles of Incorporation, Proof of Residence) makes manual standardization inefficient.

### 4. Current Impacts
| Dimension | Impact |
| :--- | :--- |
| **Operational** | Low scalability; increased demand requires linear hiring. |
| **Financial** | High cost of wasted "man-hours"; fines for missing procedural deadlines. |
| **Strategic** | Loss of competitive agility; offices delay filing actions due to triage slowness. |
| **Social** | Delay in judicial provision and release of certificates/rights. |

### 5. Consequences of NOT Acting
*   **Economic Inviability:** The operational cost of manual conference teams will make offices and notaries less competitive against players already adopting LegalTechs.
*   **Legal Risk:** Increased incidence of document frauds passing unnoticed by tired human eyes.

### 6. Risks of Investing in Resolution
*   **Technical (Hallucination):** LLMs may "hallucinate" data not present in the original document or fail with low-quality scans (poor OCR).
*   **Regulatory (LGPD):** Sensitive data treatment requires robust security infrastructure, raising development costs.
*   **Adoption Barrier:** Cultural resistance from legal professionals who distrust automated validation for solemn acts.

### 7. Knowledge Gaps (What we don't know)
*   What is the real document rejection rate due to checklist errors in an average notary?
*   What is the exact Customer Acquisition Cost (CAC) for this specific niche?
*   To what extent do current computer vision APIs (Google Vision, AWS Textract) solve handwriting reading in old documents?

### 8. Initial Hypotheses to be Tested
*   **Hypothesis 1:** Automation of conference reduces dossier triage time by at least 70%.
*   **Hypothesis 2:** Users are willing to pay a per-document fee less than 20% of the intern/paralegal hourly cost.
*   **Hypothesis 3:** AI accuracy in detecting missing checklist items is superior to human average in 8-hour shifts.

### 9. Critical Assessment
The problem is **REAL** and extremely **RELEVANT**. However, the market already has OCR and AI solutions. The competitive differential is not in "reading the document", but in "applying the business rule/checklist" in a customizable and intuitive way.

**Verdict: GO (WITH RESERVATIONS)**

**Justification:** There is pent-up demand and a billion-dollar LegalTech/GovTech market. The problem is "worthy of investment", but success depends on overcoming the technical barrier of AI accuracy and LGPD compliance.

**What still needs to be measured/proven:**
*   **Accuracy Benchmarking:** Test the tool against a real dataset of "dirty" documents (bad scans) to define the technical limit.
*   **Price Validation:** Conduct Willingness to Pay interviews with medium-sized office managers.
*   **Rules Mapping:** Identify if checklists are standardized enough to be algorithms or if they vary excessively between agencies.
