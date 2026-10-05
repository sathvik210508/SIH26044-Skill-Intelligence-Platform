import re
import io
from typing import List, Dict, Any
from rapidfuzz import fuzz, process
from pypdf import PdfReader

# Master skill ontology mapping aliases to canonical skill names
CANONICAL_SKILL_MAP = {
    # 1. Ashwagandha
    "ashwagandha": "Ashwagandha",
    "withania somnifera": "Ashwagandha",
    "indian ginseng": "Ashwagandha",
    "ashwagandha churna": "Ashwagandha",
    "python": "Ashwagandha",
    "python3": "Ashwagandha",
    "python programming": "Ashwagandha",
    "py": "Ashwagandha",

    # 2. Triphala
    "triphala": "Triphala",
    "triphala churna": "Triphala",
    "three fruits": "Triphala",
    "sql": "Triphala",
    "mysql": "Triphala",
    "postgresql": "Triphala",
    "postgres": "Triphala",
    "sqlite": "Triphala",

    # 3. Phytochemical Assay & Analysis
    "phytochemical assay & analysis": "Phytochemical Assay & Analysis",
    "phytochemical assay": "Phytochemical Assay & Analysis",
    "phytochemistry": "Phytochemical Assay & Analysis",
    "machine learning": "Phytochemical Assay & Analysis",
    "ml": "Phytochemical Assay & Analysis",
    "scikit-learn": "Phytochemical Assay & Analysis",

    # 4. HPLC Standardization & Fingerprinting
    "hplc standardization & fingerprinting": "HPLC Standardization & Fingerprinting",
    "hplc": "HPLC Standardization & Fingerprinting",
    "chromatography": "HPLC Standardization & Fingerprinting",
    "spectroscopy": "HPLC Standardization & Fingerprinting",
    "deep learning": "HPLC Standardization & Fingerprinting",
    "dl": "HPLC Standardization & Fingerprinting",
    "neural networks": "HPLC Standardization & Fingerprinting",

    # 5. Haridra
    "haridra": "Haridra",
    "curcuma longa": "Haridra",
    "react": "Haridra",
    "reactjs": "Haridra",
    "react.js": "Haridra",

    # 6. Turmeric / Curcumin
    "turmeric": "Turmeric / Curcumin",
    "turmeric / curcumin": "Turmeric / Curcumin",
    "curcumin": "Turmeric / Curcumin",
    "haldi": "Turmeric / Curcumin",
    "javascript": "Turmeric / Curcumin",
    "js": "Turmeric / Curcumin",

    # 7. Tulsi
    "tulsi": "Tulsi",
    "holy basil": "Tulsi",
    "ocimum sanctum": "Tulsi",
    "typescript": "Tulsi",
    "ts": "Tulsi",

    # 8. Guduchi / Giloy
    "giloy": "Guduchi / Giloy",
    "guduchi": "Guduchi / Giloy",
    "guduchi / giloy": "Guduchi / Giloy",
    "tinospora cordifolia": "Guduchi / Giloy",
    "c++": "Guduchi / Giloy",
    "cpp": "Guduchi / Giloy",

    # 9. Brahmi
    "brahmi": "Brahmi",
    "bacopa monnieri": "Brahmi",
    "medhya rasayana": "Brahmi",
    "java": "Brahmi",
    "core java": "Brahmi",

    # 10. Ayurvedic Pharmacopoeia Protocols (API)
    "ayurvedic pharmacopoeia protocols (api)": "Ayurvedic Pharmacopoeia Protocols (API)",
    "ayurvedic pharmacopoeia protocols": "Ayurvedic Pharmacopoeia Protocols (API)",
    "fastapi": "Ayurvedic Pharmacopoeia Protocols (API)",
    "fast api": "Ayurvedic Pharmacopoeia Protocols (API)",
    "pharmacopoeial protocols": "Ayurvedic Pharmacopoeia Protocols (API)",

    # 11. AYUSH Good Manufacturing Practice (GMP)
    "ayush good manufacturing practice (gmp)": "AYUSH Good Manufacturing Practice (GMP)",
    "ayush gmp": "AYUSH Good Manufacturing Practice (GMP)",
    "gmp": "AYUSH Good Manufacturing Practice (GMP)",
    "cloud computing": "AYUSH Good Manufacturing Practice (GMP)",
    "cloud": "AYUSH Good Manufacturing Practice (GMP)",

    # 12. Batch Quality Assurance (QA)
    "batch quality assurance (qa)": "Batch Quality Assurance (QA)",
    "quality assurance": "Batch Quality Assurance (QA)",
    "qa": "Batch Quality Assurance (QA)",
    "aws": "Batch Quality Assurance (QA)",
    "amazon web services": "Batch Quality Assurance (QA)",

    # 13. Standardized Drug Packaging & Containment
    "standardized drug packaging & containment": "Standardized Drug Packaging & Containment",
    "standardized drug packaging": "Standardized Drug Packaging & Containment",
    "drug packaging": "Standardized Drug Packaging & Containment",
    "docker": "Standardized Drug Packaging & Containment",
    "containers": "Standardized Drug Packaging & Containment",

    # 14. Ayurvedic Pharmaceutical Batch Processing
    "ayurvedic pharmaceutical batch processing": "Ayurvedic Pharmaceutical Batch Processing",
    "batch processing": "Ayurvedic Pharmaceutical Batch Processing",
    "kubernetes": "Ayurvedic Pharmaceutical Batch Processing",
    "k8s": "Ayurvedic Pharmaceutical Batch Processing",

    # 15. Pharmacovigilance & Drug Safety Monitoring
    "pharmacovigilance & drug safety monitoring": "Pharmacovigilance & Drug Safety Monitoring",
    "pharmacovigilance": "Pharmacovigilance & Drug Safety Monitoring",
    "drug safety": "Pharmacovigilance & Drug Safety Monitoring",
    "cybersecurity": "Pharmacovigilance & Drug Safety Monitoring",
    "infosec": "Pharmacovigilance & Drug Safety Monitoring",

    # 16. AYUSH Market Analytics & Consumption Trends
    "ayush market analytics & consumption trends": "AYUSH Market Analytics & Consumption Trends",
    "market analytics": "AYUSH Market Analytics & Consumption Trends",
    "power bi": "AYUSH Market Analytics & Consumption Trends",
    "powerbi": "AYUSH Market Analytics & Consumption Trends",
    "tableau": "AYUSH Market Analytics & Consumption Trends",

    # 17. Batch Manufacturing Records (BMR)
    "batch manufacturing records (bmr)": "Batch Manufacturing Records (BMR)",
    "batch manufacturing records": "Batch Manufacturing Records (BMR)",
    "bmr": "Batch Manufacturing Records (BMR)",
    "excel": "Batch Manufacturing Records (BMR)",
    "ms excel": "Batch Manufacturing Records (BMR)",

    # 18. Clinical Drug Assay & Statistical Evaluation
    "clinical drug assay & statistical evaluation": "Clinical Drug Assay & Statistical Evaluation",
    "clinical drug assay": "Clinical Drug Assay & Statistical Evaluation",
    "drug assay": "Clinical Drug Assay & Statistical Evaluation",
    "data analysis": "Clinical Drug Assay & Statistical Evaluation",
    "data science": "Clinical Drug Assay & Statistical Evaluation",
    "pandas": "Clinical Drug Assay & Statistical Evaluation",

    # 19. Automated AYUSH Formulation Intelligence
    "automated ayush formulation intelligence": "Automated AYUSH Formulation Intelligence",
    "formulation intelligence": "Automated AYUSH Formulation Intelligence",
    "genai": "Automated AYUSH Formulation Intelligence",
    "generative ai": "Automated AYUSH Formulation Intelligence",
    "llms": "Automated AYUSH Formulation Intelligence",

    # 20. Classical Ayurvedic Monograph Informatics
    "classical ayurvedic monograph informatics": "Classical Ayurvedic Monograph Informatics",
    "monograph informatics": "Classical Ayurvedic Monograph Informatics",
    "nlp": "Classical Ayurvedic Monograph Informatics",
    "natural language processing": "Classical Ayurvedic Monograph Informatics",

    # 21. Herbal Raw Material Botanical Inspection
    "herbal raw material botanical inspection": "Herbal Raw Material Botanical Inspection",
    "botanical inspection": "Herbal Raw Material Botanical Inspection",
    "computer vision": "Herbal Raw Material Botanical Inspection",
    "cv": "Herbal Raw Material Botanical Inspection",

    # 22. AYUSH Monograph & Batch Record Versioning
    "ayush monograph & batch record versioning": "AYUSH Monograph & Batch Record Versioning",
    "batch record versioning": "AYUSH Monograph & Batch Record Versioning",
    "git": "AYUSH Monograph & Batch Record Versioning",
    "github": "AYUSH Monograph & Batch Record Versioning"
}

class ResumeExtractor:
    """
    Extracts text from PDF/Text resumes, detects mentioned skills using fuzzy matching & ontology,
    normalizes skill names, and returns structured extraction items for student verification.
    """

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
            return text.strip()
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"

    def extract_skills_from_text(self, text: str) -> List[Dict[str, Any]]:
        text_lower = text.lower()
        # Clean text
        tokens = re.findall(r'[a-zA-Z0-9\+\#\.\-]+', text_lower)
        full_cleaned_text = " " + " ".join(tokens) + " "

        extracted = {}

        # 1. Exact / Substring Alias Matches
        for alias, canonical in CANONICAL_SKILL_MAP.items():
            pattern = r'(?:\b|[^a-z0-9])' + re.escape(alias) + r'(?:\b|[^a-z0-9])'
            match = re.search(pattern, full_cleaned_text)
            if match:
                # Find context snippet
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                snippet = text[start:end].replace("\n", " ").strip()
                
                if canonical not in extracted:
                    extracted[canonical] = {
                        "skill_name": canonical,
                        "detected_alias": alias,
                        "confidence": 95,
                        "snippet": f"...{snippet}..." if snippet else f"Found mention of '{alias}'",
                        "status": "Detected"
                    }

        # 2. Fuzzy Matching for skill phrases
        distinct_canonical = list(set(CANONICAL_SKILL_MAP.values()))
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines:
            line_lower = line.lower()
            if len(line_lower) > 3:
                for skill_name in distinct_canonical:
                    score = fuzz.partial_ratio(skill_name.lower(), line_lower)
                    if score >= 88 and skill_name not in extracted:
                        extracted[skill_name] = {
                            "skill_name": skill_name,
                            "detected_alias": skill_name,
                            "confidence": int(score),
                            "snippet": f"...{line[:60]}...",
                            "status": "Detected"
                        }

        # Return list of detected skills
        results = list(extracted.values())
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results

resume_extractor = ResumeExtractor()
