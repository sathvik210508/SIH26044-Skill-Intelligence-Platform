import random
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import Skill, AssessmentQuestion, AssessmentAttempt, StudentSkill
from app.ai_engine.proficiency_engine import proficiency_engine

class AssessmentService:
    """
    Adaptive assessment engine that generates tailored question sets,
    varies sequence/difficulty, calculates scores, and feeds into the Proficiency Engine.
    """

    def generate_adaptive_quiz(
        self,
        db: Session,
        skill_id: int,
        student_id: int,
        num_questions: int = 5
    ) -> Dict[str, Any]:
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            return {"error": "Skill not found"}

        questions = db.query(AssessmentQuestion).filter(AssessmentQuestion.skill_id == skill_id).all()
        
        # If questions in DB are sparse, provide realistic fallbacks
        if len(questions) < num_questions:
            pool = self._get_fallback_questions(skill.name)
        else:
            pool = [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "options": q.options_json,
                    "difficulty": q.difficulty_level,
                    "correct_index": q.correct_option_index,
                    "explanation": q.explanation
                }
                for q in questions
            ]

        # Categorize by difficulty for adaptive sequence
        easy_q = [q for q in pool if q.get("difficulty") == "Easy"]
        med_q = [q for q in pool if q.get("difficulty") == "Medium"]
        hard_q = [q for q in pool if q.get("difficulty") == "Hard"]

        # If categories are empty, treat all as med
        if not easy_q: easy_q = pool
        if not med_q: med_q = pool
        if not hard_q: hard_q = pool

        selected = []
        # Adaptive template: 1 Easy -> 2 Med -> 2 Hard
        selected.extend(random.sample(easy_q, min(1, len(easy_q))))
        remaining_med = [q for q in med_q if q not in selected]
        selected.extend(random.sample(remaining_med, min(2, len(remaining_med))))
        remaining_hard = [q for q in hard_q if q not in selected]
        selected.extend(random.sample(remaining_hard, min(2, len(remaining_hard))))

        # If still short, sample from full pool
        while len(selected) < num_questions and len(pool) > len(selected):
            extra = random.choice([q for q in pool if q not in selected])
            selected.append(extra)

        # Shuffle selected questions to avoid identical sequences
        random.shuffle(selected)

        # Shuffle options for each question, adjusting correct_index
        sanitized_questions = []
        answers_key = {}
        for idx, q in enumerate(selected):
            opts = list(q["options"])
            orig_correct = q["correct_index"]
            correct_text = opts[orig_correct] if orig_correct < len(opts) else opts[0]
            
            # Shuffle options
            random.shuffle(opts)
            new_correct_idx = opts.index(correct_text)
            
            q_id = f"q_{idx+1}"
            answers_key[q_id] = {
                "correct_index": new_correct_idx,
                "explanation": q.get("explanation", "Correct application of core concept.")
            }

            sanitized_questions.append({
                "question_id": q_id,
                "question_text": q["question_text"],
                "options": opts,
                "difficulty": q.get("difficulty", "Medium")
            })

        return {
            "skill_id": skill.id,
            "skill_name": skill.name,
            "total_questions": len(sanitized_questions),
            "time_limit_minutes": 10,
            "questions": sanitized_questions,
            "answers_key": answers_key  # Stored in session or returned for verification
        }

    def submit_and_grade_quiz(
        self,
        db: Session,
        student_id: int,
        skill_id: int,
        student_answers: Dict[str, int],  # {"q_1": 2, "q_2": 0, ...}
        answers_key: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        skill = db.query(Skill).filter(Skill.id == skill_id).first()
        if not skill:
            return {"error": "Skill not found"}

        total = len(answers_key)
        correct_count = 0
        details = []

        for q_id, key_info in answers_key.items():
            correct_idx = key_info["correct_index"]
            chosen_idx = student_answers.get(q_id, -1)
            is_correct = (chosen_idx == correct_idx)
            if is_correct:
                correct_count += 1
            details.append({
                "question_id": q_id,
                "chosen_index": chosen_idx,
                "correct_index": correct_idx,
                "is_correct": is_correct,
                "explanation": key_info.get("explanation", "")
            })

        score_pct = round((correct_count / total * 100.0), 1) if total > 0 else 0.0
        passed = score_pct >= 50.0

        # Record attempt
        attempt = AssessmentAttempt(
            student_id=student_id,
            skill_id=skill_id,
            score=score_pct,
            total_questions=total,
            correct_answers=correct_count,
            passed=passed,
            details_json=details
        )
        db.add(attempt)

        # Update or create StudentSkill
        st_skill = db.query(StudentSkill).filter(
            StudentSkill.student_id == student_id,
            StudentSkill.skill_id == skill_id
        ).first()

        if not st_skill:
            st_skill = StudentSkill(
                student_id=student_id,
                skill_id=skill_id,
                test_score=score_pct,
                source="Assessment",
                status="Verified"
            )
            db.add(st_skill)
        else:
            st_skill.test_score = score_pct
            st_skill.status = "Verified"

        db.flush()

        # Recalculate proficiency using central ProficiencyEngine
        calc = proficiency_engine.calculate_proficiency(
            test_score=st_skill.test_score,
            practical_score=st_skill.practical_score,
            verified_score=st_skill.verified_score,
            course_score=st_skill.course_score
        )
        st_skill.proficiency_score = calc["proficiency_score"]
        st_skill.evidence_breakdown = calc
        db.commit()

        return {
            "skill_name": skill.name,
            "score": score_pct,
            "correct_answers": correct_count,
            "total_questions": total,
            "passed": passed,
            "new_overall_proficiency": calc["proficiency_score"],
            "breakdown": calc["breakdown_explanation"],
            "details": details
        }

    def _get_fallback_questions(self, skill_name: str) -> List[Dict[str, Any]]:
        s = skill_name.lower()
        if "ashwagandha" in s or "python" in s:
            return [
                {
                    "question_text": "Which primary active chemical constituents are responsible for the adaptogenic and therapeutic bioactivity of Ashwagandha (Withania somnifera)?",
                    "options": ["Withanolides and Withaferin A", "Curcuminoids", "Bacosides A and B", "Guggulsterones"],
                    "difficulty": "Easy",
                    "correct_index": 0,
                    "explanation": "Withanolides (steroidal lactones) including Withaferin A are the primary bioactive constituents of Ashwagandha."
                },
                {
                    "question_text": "In classical Ayurvedic pharmacology, what is the primary Rasayana classification and therapeutic action of Ashwagandha?",
                    "options": ["Balya and Medhya Rasayana (vitality and nervous system rejuvenator)", "Deepana and Pachana (appetite stimulant only)", "Virechana Dravya (purgative)", "Sheetala Stambhana (cooling astringent)"],
                    "difficulty": "Medium",
                    "correct_index": 0,
                    "explanation": "Ashwagandha is classically categorized as a Balya (strength-promoting) and Rasayana (rejuvenating) herb that pacifies Vata and Kapha."
                },
                {
                    "question_text": "How does Ashwagandha exert its neuroprotective and adaptogenic effects against chronic physiological stress?",
                    "options": [
                        "Modulates the hypothalamic-pituitary-adrenal (HPA) axis and reduces serum cortisol levels",
                        "Induces permanent central nervous system depression",
                        "Bypasses cellular receptor pathways without metabolic transformation",
                        "Inhibits total protein synthesis across skeletal muscle"
                    ],
                    "difficulty": "Hard",
                    "correct_index": 0,
                    "explanation": "Ashwagandha acts on the HPA axis to regulate cortisol synthesis and support endocrine resilience under stress."
                },
                {
                    "question_text": "Which plant part of Withania somnifera is traditionally harvested and processed into standard therapeutic Churna or Ksheerapaka?",
                    "options": ["Moola (Dried Roots)", "Patra (Leaves only)", "Phala (Fresh Berries)", "Pushpa (Flowers)"],
                    "difficulty": "Easy",
                    "correct_index": 0,
                    "explanation": "The root (Moola) is the primary official part used in Ayurvedic formulations of Ashwagandha."
                },
                {
                    "question_text": "Which traditional Ayurvedic vehicle (Anupana) is clinically recommended to enhance the bio-assimilation of Ashwagandha Churna for Rasayana benefits?",
                    "options": [
                        "Godugdha (Warm Cow's Milk) or Ghrita (Ghee)",
                        "Cold alkaline water",
                        "Acidic citrus fruit juice",
                        "Fermented alcohol without dilution"
                    ],
                    "difficulty": "Hard",
                    "correct_index": 0,
                    "explanation": "Warm milk (Godugdha) and Ghee (Ghrita) serve as lipid-based Anupana enhancing lipid-soluble withanolide absorption."
                }
            ]
        elif "triphala" in s or "sql" in s:
            return [
                {
                    "question_text": "Which classical trio of Ayurvedic myrobalan fruits constitutes the traditional formulation of Triphala?",
                    "options": ["Amalaki, Bibhitaki, and Haritaki", "Ashwagandha, Shatavari, and Giloy", "Pippali, Maricha, and Shunthi", "Neem, Tulsi, and Brahmi"],
                    "difficulty": "Easy",
                    "correct_index": 0,
                    "explanation": "Triphala is composed of Amalaki (Emblica officinalis), Bibhitaki (Terminalia bellirica), and Haritaki (Terminalia chebula)."
                },
                {
                    "question_text": "What is the standard classical ratio of Haritaki, Bibhitaki, and Amalaki in standard Triphala Churna according to the Ayurvedic Formulary of India (AFI)?",
                    "options": [
                        "Equal parts (1:1:1 by dry fruit weight)",
                        "4:2:1 unequal parts",
                        "1:2:4 inverse weight ratio",
                        "10:1:1 concentrated extract"
                    ],
                    "difficulty": "Medium",
                    "correct_index": 0,
                    "explanation": "The Ayurvedic Formulary of India (AFI) specifies equal proportions (1:1:1) of the three dried pericarp powders."
                },
                {
                    "question_text": "How does Triphala uniquely balance the three physiological humors (Tridosha) in Ayurvedic therapeutics?",
                    "options": [
                        "Amalaki pacifies Pitta, Bibhitaki pacifies Kapha, and Haritaki pacifies Vata",
                        "It pacifies only Vata and aggravates Pitta",
                        "It acts strictly on Kapha dosha while remaining neutral to others",
                        "It eliminates all doshas indiscriminately"
                    ],
                    "difficulty": "Hard",
                    "correct_index": 0,
                    "explanation": "Each of the three fruits targets a specific dosha: Haritaki pacifies Vata, Bibhitaki balances Kapha, and Amalaki pacifies Pitta."
                },
                {
                    "question_text": "What is the primary gastrointestinal clinical application of Triphala Churna when administered with warm water at bedtime?",
                    "options": ["Mild Anulomana (bowel regulation and gentle laxative)", "Deep emetic purging", "Suppression of digestive fire", "Stomach acid over-secretion"],
                    "difficulty": "Easy",
                    "correct_index": 0,
                    "explanation": "Triphala acts as an Anulomana herb, promoting natural peristalsis and gentle digestive regulation."
                },
                {
                    "question_text": "Which high-concentration natural antioxidant compounds in Triphala provide its potent cytoprotective and Chakshushya (ocular health) benefits?",
                    "options": [
                        "Tannins, Gallic acid, Ellagic acid, and Vitamin C (Ascorbic acid)",
                        "Saturated fatty acid polymers",
                        "Inorganic salt crystals",
                        "Synthetic mineral chelates"
                    ],
                    "difficulty": "Medium",
                    "correct_index": 0,
                    "explanation": "Triphala is rich in polyphenols, gallic acid, ellagic acid, and ascorbic acid conferring robust antioxidant and cytoprotective properties."
                }
            ]
        else: # Generic AYUSH Medicine / Formulation Principles
            return [
                {
                    "question_text": f"What is the foundational pharmacopoeial quality principle of {skill_name}?",
                    "options": [
                        "Standardization of active phytochemical markers, botanical authentication, and safety testing",
                        "Unstandardized raw material collection without batch documentation",
                        "Omitting microbial and heavy metal limit testing",
                        "Random formulation without classical reference texts"
                    ],
                    "difficulty": "Easy",
                    "correct_index": 0,
                    "explanation": "Ayurvedic Pharmacopoeia standards require rigorous botanical authentication, marker standardization, and limits testing."
                },
                {
                    "question_text": f"When scaling the pharmaceutical manufacturing of {skill_name}, which regulatory protocol ensures consistent batch potency?",
                    "options": [
                        "AYUSH Good Manufacturing Practice (GMP) with in-process quality control (IPQC) and validated batch records",
                        "Unregulated mass production without standard operating procedures",
                        "Skipping accelerated stability testing",
                        "Varying solvent ratios arbitrarily across batches"
                    ],
                    "difficulty": "Medium",
                    "correct_index": 0,
                    "explanation": "Strict adherence to AYUSH GMP guidelines and validated batch records guarantees therapeutic consistency across production lots."
                },
                {
                    "question_text": f"Which pharmacognostic and laboratory method ensures freedom from contamination in {skill_name}?",
                    "options": [
                        "Atomic Absorption Spectroscopy for heavy metals, aflatoxin HPLC assay, and microbial load enumeration",
                        "Visual inspection of raw powder without quantitative lab testing",
                        "Omitting pesticide residue screening",
                        "Storing raw herbs in humid non-climate controlled rooms"
                    ],
                    "difficulty": "Hard",
                    "correct_index": 0,
                    "explanation": "Comprehensive quality assurance mandates heavy metal analysis, pesticide residue screening, and microbiological limits."
                },
                {
                    "question_text": f"What is the recommended method to verify the shelf-life and chemical stability of {skill_name} formulations?",
                    "options": [
                        "ICH / AYUSH stability testing guidelines evaluating active phytochemical degradation under real-time and accelerated conditions",
                        "Subjective visual estimation after 2 years",
                        "Relying strictly on historical folklore without analytical testing",
                        "Omitting packaging compatibility evaluations"
                    ],
                    "difficulty": "Medium",
                    "correct_index": 0,
                    "explanation": "Accelerated and real-time stability protocols establish official expiration dates and degradation kinetics for AYUSH drugs."
                },
                {
                    "question_text": f"In classical Ayurvedic pharmaceutics (Bhaishajya Kalpana), how is the therapeutic bioavailability of {skill_name} optimized?",
                    "options": [
                        "Selection of classical Anupana (carrier mediums like honey, milk, or ghee) and synergistic adjuvant herbs",
                        "Administering raw unprocessed material without purificatory Samskaras",
                        "Combining with antagonistic (Viruddha) dietary agents",
                        "Omitting standardized particle size micronization"
                    ],
                    "difficulty": "Easy",
                    "correct_index": 0,
                    "explanation": "Appropriate Anupana and classical pharmaceutical processing (Samskara) maximize active compound assimilation and targeted delivery."
                }
            ]

assessment_service = AssessmentService()
