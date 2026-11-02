from pydantic import BaseModel, Field
from typing import List, Optional

class Party(BaseModel):
    name: str
    role: str  # "Promoter", "Purchaser", "POA", "Witness"
    age: Optional[int] = None
    pan: Optional[str] = None
    aadhaar_masked: Optional[str] = None
    address: Optional[str] = None

class PropertyDetails(BaseModel):
    flat_no: str
    floor: str
    wing: Optional[str] = None
    building_name: str
    carpet_area_sqmt: float
    carpet_area_sqft: Optional[float] = None
    parking: Optional[str] = None
    plot_no: str
    plot_area_sqmt: Optional[float] = None
    sector_no: str
    node_village: str
    taluka: str
    district: str
    boundaries: Optional[dict] = Field(default_factory=dict)

class RegistrationDetails(BaseModel):
    sub_registrar_office: str
    document_no: str
    receipt_no: Optional[str] = None
    registration_date: str
    execution_date: str
    consideration_amount: float
    market_value: float
    stamp_duty_paid: float
    registration_fee_paid: float
    gras_challan_grn: Optional[str] = None

class ApprovalRecord(BaseModel):
    authority: str  # "CIDCO", "Panvel Municipal Corporation", "MahaRERA", "MMRDA"
    document_type: str  # "Allotment Letter", "Agreement to Lease", "CC", "Amended CC", "RERA Certificate"
    reference_no: str
    date: str
    valid_upto: Optional[str] = None
    notes: Optional[str] = None

class DevolutionStage(BaseModel):
    title: str
    date: str
    description: str

class SearchYearRecord(BaseModel):
    year: int
    entry_summary: str
    records_checked: str = "Available Records Checked"
    has_encumbrance: bool = False

class TitleInvestigationData(BaseModel):
    advocate_name: str = "Adv. Anandkumar M. Mishra (JM Associates)"
    advocate_details: str = "B.L.S., LL.B., Mob: 9004836678 / 9594846678, Office No. 49, Vindhya Complex, Sec-11, CBD Belapur, Navi Mumbai"
    bank_name: str = "LIC Housing Finance Ltd."
    bank_branch: str = "Panvel, Tal. Panvel, Dist. Raigad"
    report_ref_no: str = "JM/LIC/10/78/2026"
    report_date: str = "18/10/2026"
    loan_account_no: Optional[str] = "6001050004992"
    ref_no: Optional[str] = "6001210003184"
    
    property: PropertyDetails
    registration: RegistrationDetails
    promoter: Party
    purchasers: List[Party]
    approvals: List[ApprovalRecord]
    devolution_chain: List[DevolutionStage]
    search_years: List[SearchYearRecord]
    schedule_1_docs_examined: List[str]
    schedule_2_required_originals: List[dict]
    title_certificate_text: str
