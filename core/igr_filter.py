"""
IGR Maharashtra Smart Filter & Fraud Detection Engine
Solves the client's core problem: Filtering thousands of noisy IGR results down to exact matches
and detecting suspicious transactions, duplicate mortgages, and name mutations.
"""

from typing import List, Dict, Any
from rapidfuzz import fuzz
import re

class IGRSmartFilter:
    def __init__(self, target_flat: str, target_floor: str, target_building: str,
                 target_plot: str, target_sector: str, target_parties: List[str]):
        self.target_flat = str(target_flat).strip()
        self.target_floor = str(target_floor).strip()
        self.target_building = target_building.strip().lower()
        self.target_plot = str(target_plot).strip()
        self.target_sector = str(target_sector).strip()
        self.target_parties = [p.strip().lower() for p in target_parties if p]

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        # normalize common abbreviations
        text = text.lower()
        text = text.replace("chs", "co operative housing society")
        text = text.replace("soc", "society")
        text = text.replace("sec", "sector")
        text = text.replace("flt", "flat")
        text = text.replace("plt", "plot")
        return text

    def score_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scores an IGR entry against the target criteria.
        Returns relevance category:
        - DIRECT_CHAIN_MATCH: Matches flat no, building, parties
        - CONVEYANCE_RECORD: Society-level conveyance (flat no omitted)
        - NOTICE_OF_INTIMATION: Bank mortgage charge
        - SUSPICIOUS_CONFLICT: Same flat/floor but different purchaser/seller (potential fraud/double sale!)
        - IRRELEVANT_NOISE: Different flat in the same plot/sector
        """
        prop_desc = self.normalize(entry.get("property_description", ""))
        parties = self.normalize(" ".join(entry.get("parties", [])))
        doc_type = self.normalize(entry.get("doc_type", ""))
        
        # 1. Flat Number Extraction & Match
        flat_match = False
        flat_pattern = r'\b(?:flat|flat no|sadanika|सदनिका|room|f-)\s*[:.-]?\s*' + re.escape(self.target_flat) + r'\b'
        exact_num_pattern = r'\b' + re.escape(self.target_flat) + r'\b'
        
        if re.search(flat_pattern, prop_desc) or (re.search(exact_num_pattern, prop_desc) and "plot" not in prop_desc[max(0, prop_desc.find(self.target_flat)-10):prop_desc.find(self.target_flat)]):
            flat_match = True

        # 2. Building / Society Match
        building_score = fuzz.partial_ratio(self.target_building, prop_desc)
        building_match = building_score > 70

        # 3. Party Match
        party_match_score = 0
        matched_party = None
        for p in self.target_parties:
            score = fuzz.partial_ratio(p, parties)
            if score > party_match_score:
                party_match_score = score
                matched_party = p
        has_party_match = party_match_score > 75

        # 4. Check for Notice of Intimation (Bank Mortgage)
        is_noi = "notice of intimation" in doc_type or "intimation" in doc_type or "mortgage" in doc_type or "noi" in doc_type

        # 5. Check for Deemed Conveyance / Society Handover
        is_conveyance = "deemed conveyance" in doc_type or "conveyance" in doc_type or "अभिहस्तांतरण" in doc_type or "society" in parties

        # Categorization Logic
        if flat_match:
            if has_party_match:
                category = "DIRECT_CHAIN_MATCH"
                risk_level = "CLEAN"
                explanation = f"Matches Flat {self.target_flat} and verified party '{matched_party}'."
            elif is_noi:
                category = "NOTICE_OF_INTIMATION"
                risk_level = "REQUIRES_VERIFICATION"
                explanation = f"Bank charge / Notice of Intimation detected on Flat {self.target_flat}. Verify mortgage release/NOC."
            else:
                category = "SUSPICIOUS_CONFLICT"
                risk_level = "HIGH_ALERT"
                explanation = f"CRITICAL: Transaction found on Flat {self.target_flat} with DIFFERENT parties! Check for duplicate sale / forgery."
        elif is_conveyance and building_match:
            category = "CONVEYANCE_RECORD"
            risk_level = "INFO"
            explanation = "Society Conveyance deed detected. Rights transferred from builder to society."
        elif is_noi and building_match:
            category = "NOTICE_OF_INTIMATION"
            risk_level = "REQUIRES_VERIFICATION"
            explanation = "Notice of Intimation recorded at project/plot level. Verify if this flat was released."
        else:
            category = "IRRELEVANT_NOISE"
            risk_level = "IGNORED"
            explanation = "Different flat or unrelated unit in the same plot/sector."

        result = dict(entry)
        result["category"] = category
        result["risk_level"] = risk_level
        result["explanation"] = explanation
        result["building_match_score"] = building_score
        result["party_match_score"] = party_match_score
        result["is_relevant"] = category != "IRRELEVANT_NOISE"
        return result

    def filter_and_rank(self, raw_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process an entire raw batch from IGR and partition into Actionable vs Noise."""
        scored = [self.score_entry(e) for e in raw_entries]
        
        relevant_entries = [e for e in scored if e["is_relevant"]]
        noise_entries = [e for e in scored if not e["is_relevant"]]
        high_alerts = [e for e in scored if e["risk_level"] == "HIGH_ALERT"]
        
        return {
            "total_raw_entries": len(raw_entries),
            "relevant_count": len(relevant_entries),
            "noise_filtered_out_count": len(noise_entries),
            "high_alert_count": len(high_alerts),
            "relevant_records": sorted(relevant_entries, key=lambda x: (x["risk_level"] == "HIGH_ALERT", x["year"]), reverse=True),
            "noise_summary": f"Automatically eliminated {len(noise_entries)} unrelated entries for other flats in Sector {self.target_sector}, Plot {self.target_plot}."
        }
