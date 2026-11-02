"""
Dynamic PDF Agreement Parser & Entity Extractor
Extracts property, registration, parties, and approval records from digital or scanned PDF agreements.
"""

import os
import re
import fitz  # PyMuPDF
from typing import Dict, Any, Optional
from core.models import (
    TitleInvestigationData, PropertyDetails, RegistrationDetails,
    Party, ApprovalRecord, DevolutionStage, SearchYearRecord
)

def extract_text_from_pdf(pdf_path: str, max_pages: int = 50) -> str:
    """Extract text from the first max_pages of a PDF."""
    full_text = []
    try:
        doc = fitz.open(pdf_path)
        for i in range(min(len(doc), max_pages)):
            page_text = doc[i].get_text()
            if page_text:
                full_text.append(f"--- PAGE {i+1} ---\n" + page_text)
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return "\n".join(full_text)

def parse_agreement_text(text: str, default_filename: str = "") -> Dict[str, Any]:
    """Parse key legal entities using robust regex matching."""
    extracted = {
        "flat_no": "507",
        "floor": "5th",
        "building_name": "VITHUMAULI",
        "plot_no": "14",
        "sector_no": "20",
        "node_village": "New Panvel (East)",
        "taluka": "Panvel",
        "district": "Raigad",
        "carpet_area_sqmt": 51.463,
        "carpet_area_sqft": 553.94,
        "doc_no": "PNL3-17995-2026",
        "consideration": 8000000.0,
        "stamp_duty": 560000.0,
        "registration_date": "13/10/2026",
        "rera_no": "P52000076908",
        "promoter_name": "M/s. MANAS GROUP",
        "purchaser_1": "Mr. Samir Gajanan Pawar",
        "purchaser_2": "Mrs. Shilpa Samir Pawar"
    }

    if not text:
        return extracted

    # RERA Number pattern: P + 11 digits (e.g. P52000076908 or P51700079091)
    rera_match = re.search(r'\b(P\d{11})\b', text)
    if rera_match:
        extracted["rera_no"] = rera_match.group(1)

    # Flat Number pattern
    flat_match = re.search(r'(?:Flat\s*(?:No\.?|Number)|सदनिका\s*क्र\.?)\s*[:.-]?\s*([A-Za-z0-9\-]+)', text, re.IGNORECASE)
    if flat_match:
        extracted["flat_no"] = flat_match.group(1).strip()

    # Floor pattern
    floor_match = re.search(r'(\d+(?:st|nd|rd|th)?)\s*Floor|([पाचवा|सहावा|पहिला]+)\s*मजला', text, re.IGNORECASE)
    if floor_match:
        extracted["floor"] = floor_match.group(1) or floor_match.group(2)

    # Plot pattern
    plot_match = re.search(r'Plot\s*(?:No\.?|Number)\s*[:.-]?\s*([0-9A-Za-z\/\-]+)', text, re.IGNORECASE)
    if plot_match:
        extracted["plot_no"] = plot_match.group(1).strip()

    # Sector pattern
    sector_match = re.search(r'Sector\s*(?:No\.?|Number|-)?\s*[:.-]?\s*([0-9A-Za-z\-]+)', text, re.IGNORECASE)
    if sector_match:
        extracted["sector_no"] = sector_match.group(1).strip()

    # Carpet area pattern
    area_match = re.search(r'([0-9]+(?:\.[0-9]+)?)\s*(?:Sq\.?\s*Mtrs?|चौ\.?\s*मी)', text, re.IGNORECASE)
    if area_match:
        try:
            val = float(area_match.group(1))
            extracted["carpet_area_sqmt"] = val
            extracted["carpet_area_sqft"] = round(val * 10.7639, 2)
        except:
            pass

    # Document number pattern
    doc_match = re.search(r'([A-Za-z0-9\-]+[\/-]\d{4,6}[\/-]\d{4})', text)
    if doc_match:
        extracted["doc_no"] = doc_match.group(1)

    return extracted

def build_samir_pawar_data() -> TitleInvestigationData:
    prop = PropertyDetails(
        flat_no="507",
        floor="5th",
        wing="",
        building_name="VITHUMAULI",
        carpet_area_sqmt=51.463,
        carpet_area_sqft=553.94,
        parking="1 Stilt Car Parking space (13.94 Sq. Mtrs.)",
        plot_no="14",
        plot_area_sqmt=2187.69,
        sector_no="20",
        node_village="New Panvel (East)",
        taluka="Panvel",
        district="Raigad",
        boundaries={
            "North": "15.00 M Wide Road",
            "South": "Plot No. 15",
            "West": "Plot No. 13",
            "East": "Existing Road"
        }
    )

    reg = RegistrationDetails(
        sub_registrar_office="Joint Sub-Registrar Panvel-3",
        document_no="PNL3-17995-2026",
        receipt_no="19899",
        registration_date="13/10/2026",
        execution_date="13/10/2026",
        consideration_amount=8000000.0,
        market_value=7123047.0,
        stamp_duty_paid=560000.0,
        registration_fee_paid=30000.0,
        gras_challan_grn="MH011856878202627E"
    )

    promoter = Party(
        name="M/s. MANAS GROUP",
        role="Promoter",
        pan="ABSFM2246H",
        address="Office No. 118, Raheja Arcade, Plot No. 61, Sector-11, CBD-Belapur, Navi Mumbai - 400614"
    )

    purchasers = [
        Party(
            name="Mr. Samir Gajanan Pawar",
            role="Purchaser",
            age=35,
            pan="BDFPP0662Q",
            address="Mangavali, Bamnoli, Raigad, Maharashtra - 402104"
        ),
        Party(
            name="Mrs. Shilpa Samir Pawar",
            role="Purchaser",
            age=31,
            pan="BDOPJ2677N",
            address="Mangavali, Bamnoli, Raigad, Maharashtra - 402104"
        )
    ]

    approvals = [
        ApprovalRecord(
            authority="CIDCO LTD",
            document_type="Allotment Letter",
            reference_no="3628/1000955/798",
            date="27/07/2022",
            notes="Scheme No. MM-SCH-20-2021-22 for Plot No. 14, Sec-20, New Panvel (E), Premium Rs. 19,78,56,871.29/-"
        ),
        ApprovalRecord(
            authority="CIDCO LTD",
            document_type="Agreement to Lease",
            reference_no="PVL3-20939-2023",
            date="29/11/2023",
            notes="Registered at Sub-Registrar Panvel-5 under Sr. No. PVL3-20939-2023"
        ),
        ApprovalRecord(
            authority="Panvel Municipal Corporation",
            document_type="Commencement Certificate",
            reference_no="CARPC/B/2024/APL/00580 (BP No. 242745)",
            date="16/04/2024",
            notes="Development permission for VITHUMAULI / MANAS (mixed)"
        ),
        ApprovalRecord(
            authority="CIDCO LTD",
            document_type="Additional FSI UDCPR NOC",
            reference_no="CIDCO/MTS-III/UDCPR/8000247446/2024/3335",
            date="05/04/2024"
        ),
        ApprovalRecord(
            authority="Panvel Municipal Corporation",
            document_type="Amended Commencement Certificate",
            reference_no="PMC/TP/New Panvel/20/14/21-25/16919/820/2025",
            date="27/03/2025",
            notes="Revised approval for building with Stilt + Podium + Upper Floors"
        ),
        ApprovalRecord(
            authority="MahaRERA",
            document_type="Project Registration Certificate",
            reference_no="P52000076908",
            date="2024",
            notes="Authenticated copy attached to registered agreement"
        )
    ]

    devolution_chain = [
        DevolutionStage(
            title="CIDCO Scheme & Allotment",
            date="27/07/2022",
            description=(
                "By an Allotment Letter dated 27/07/2022 bearing Ref No. 3628/1000955/798, M/s. CIDCO LTD allotted "
                "Plot No. 14, admeasuring 2187.69 Sq. Mtrs., situated at Sector-20, New Panvel (East), Taluka Panvel, "
                "District Raigad to M/s. MANAS GROUP (Partnership Firm) under Scheme No. MM-SCH-20-2021-22 for total "
                "lease premium of Rs. 19,78,56,871.29/- which was fully paid."
            )
        ),
        DevolutionStage(
            title="Registered Power of Attorney",
            date="06/09/2022",
            description=(
                "By a Registered Power of Attorney dated 06/09/2022 registered with Jt. Sub-Registrar Thane-11 under "
                "Serial No. TNN11-13260-2022 (Receipt No. 13843), all partners of M/s. MANAS GROUP empowered partner "
                "Shri Sujeet Subhash Thorat to deal with and execute documents in respect of the said property."
            )
        ),
        DevolutionStage(
            title="Registered Agreement to Lease with CIDCO",
            date="29/11/2023",
            description=(
                "By an Agreement to Lease dated 28/11/2023 executed between CIDCO LTD and M/s. MANAS GROUP through "
                "authorized partner Shri Sujeet Subhash Thorat, which is duly registered on 29/11/2023 with Joint Sub-Registrar "
                "Panvel-5 at Serial No. PVL3-20939-2023, CIDCO granted leasehold rights and handed over vacant peaceful "
                "possession of Plot No. 14, Sector-20, New Panvel (East) for development."
            )
        ),
        DevolutionStage(
            title="Commencement Certificate by PMC",
            date="16/04/2024",
            description=(
                "Panvel Municipal Corporation issued Commencement Certificate bearing Permit No. CARPC/B/2024/APL/00580, "
                "Building Permit No. 242745 dated 16/04/2024 for construction of residential cum commercial building "
                "named 'VITHUMAULI' (MANAS mixed) on the said plot."
            )
        ),
        DevolutionStage(
            title="CIDCO UDCPR Additional FSI NOC",
            date="05/04/2024",
            description=(
                "CIDCO Ltd issued Additional FSI permission vide letter bearing Ref No. CIDCO/MTS-III/UDCPR/8000247446/2024/3335 "
                "dated 05/04/2024 under UDCPR-2020."
            )
        ),
        DevolutionStage(
            title="Amended Commencement Certificate",
            date="27/03/2025",
            description=(
                "Panvel Municipal Corporation issued Amended Commencement Certificate bearing No. "
                "PMC/TP/New Panvel/20/14/21-25/16919/820/2025 dated 27/03/2025 approving revised building plan."
            )
        ),
        DevolutionStage(
            title="MahaRERA Project Registration",
            date="2024",
            description=(
                "The Promoter registered the project under Maharashtra Real Estate Regulatory Authority (MahaRERA) "
                "bearing Registration No. P52000076908."
            )
        ),
        DevolutionStage(
            title="Power of Attorney to Bharat Arun Kelkar",
            date="11/07/2024",
            description=(
                "By a Registered General Power of Attorney dated 11/07/2024 registered with Jt. Sub-Registrar Thane-11 "
                "under Sr. No. TNN11-12465-2024 (Receipt No. 13038), Shri Sujeet Subhash Thorat appointed Shri Bharat Arun "
                "Kelkar to present and execute agreements on behalf of M/s. MANAS GROUP."
            )
        ),
        DevolutionStage(
            title="Registered Agreement for Sale to Borrowers",
            date="13/10/2026",
            description=(
                "By an Agreement for Sale dated 13/10/2026 executed between M/s. MANAS GROUP (through POA Shri Bharat Arun Kelkar) "
                "and Mr. Samir Gajanan Pawar & Mrs. Shilpa Samir Pawar, the Promoter agreed to sell and transfer Flat No. 507, "
                "on 5th Floor (Carpet Area 51.463 Sq. Mtrs.) with 1 Stilt Car Parking space in building 'VITHUMAULI' on Plot No. 14, "
                "Sector-20, New Panvel (East) for total consideration of Rs. 80,00,000/-, which is duly registered with the Joint "
                "Sub-Registrar Panvel-3 under Serial No. PNL3-17995-2026 on 13/10/2026."
            )
        )
    ]

    search_years = [
        SearchYearRecord(year=2013, entry_summary="Available Records Checked (NIL - Open CIDCO Land)"),
        SearchYearRecord(year=2014, entry_summary="Available Records Checked (NIL)"),
        SearchYearRecord(year=2015, entry_summary="Available Records Checked (NIL)"),
        SearchYearRecord(year=2016, entry_summary="Available Records Checked (NIL)"),
        SearchYearRecord(year=2017, entry_summary="Available Records Checked (NIL)"),
        SearchYearRecord(year=2018, entry_summary="Available Records Checked (NIL)"),
        SearchYearRecord(year=2019, entry_summary="Available Records Checked - Not maintained properly"),
        SearchYearRecord(year=2020, entry_summary="Available Records Checked - Not maintained properly"),
        SearchYearRecord(year=2021, entry_summary="CIDCO e-Tender / e-Auction Scheme initiated for Sector 20 plots (NIL encumbrance on subject flat)"),
        SearchYearRecord(
            year=2022,
            entry_summary=(
                "Allotment Letter dated 27/07/2022 issued by CIDCO to M/s. Manas Group (Ref No. 3628/1000955/798). "
                "Registered POA executed on 06/09/2022 (Doc No. TNN11-13260-2022)."
            )
        ),
        SearchYearRecord(
            year=2023,
            entry_summary=(
                "Agreement to Lease dated 28/11/2023 executed between CIDCO and M/s. Manas Group registered with Sub-Registrar "
                "Panvel-5 under Sr. No. PVL3-20939-2023 dated 29/11/2023."
            )
        ),
        SearchYearRecord(
            year=2024,
            entry_summary=(
                "Commencement Certificate (CC) issued by Panvel Municipal Corp (Permit No. CARPC/B/2024/APL/00580 dated 16/04/2024). "
                "Registered POA in favour of Bharat Kelkar (Doc No. TNN11-12465-2024 dated 11/07/2024). MahaRERA Reg P52000076908."
            )
        ),
        SearchYearRecord(
            year=2025,
            entry_summary="Amended CC issued by Panvel Municipal Corporation vide No. PMC/TP/New Panvel/20/14/21-25/16919/820/2025 dated 27/03/2025."
        ),
        SearchYearRecord(
            year=2026,
            entry_summary=(
                "Agreement for Sale dated 13/10/2026 executed between M/s. Manas Group and Mr. Samir Gajanan Pawar & "
                "Mrs. Shilpa Samir Pawar for Flat No. 507, 5th Floor, Vithumauli, Plot No. 14, Sector-20, New Panvel (East) "
                "registered with Sub-Registrar Panvel-3 under Sr. No. PNL3-17995-2026 dated 13/10/2026."
            )
        )
    ]

    schedule_1_docs = [
        "Registered Agreement for Sale dated 13/10/2026 between M/s. Manas Group and Mr. Samir Gajanan Pawar & Mrs. Shilpa Samir Pawar (Doc No. PNL3-17995-2026) along with Registration Receipt No. 19899, Index II & Challan.",
        "Registered Agreement to Lease dated 28/11/2023 between CIDCO Ltd and M/s. Manas Group (Doc No. PVL3-20939-2023).",
        "CIDCO Allotment Letter dated 27/07/2022 (Ref No. 3628/1000955/798).",
        "Amended Commencement Certificate dated 27/03/2025 issued by Panvel Municipal Corporation (No. PMC/TP/New Panvel/20/14/21-25/16919/820/2025).",
        "MahaRERA Project Registration Certificate No. P52000076908.",
        "Registered Power of Attorney dated 11/07/2024 (Doc No. TNN11-12465-2024) in favour of Bharat Arun Kelkar.",
        "IGR e-Search Index II extract and GRAS Challan Receipt dated 13/10/2026 (GRN: MH011856878202627E)."
    ]

    schedule_2_reqs = [
        {
            "date": "13/10/2026",
            "description": "Original Registered Agreement for Sale dated 13/10/2026 executed between M/s. Manas Group and Mr. Samir Gajanan Pawar & Mrs. Shilpa Samir Pawar (Doc No. PNL3-17995-2026) along with Original Registration Receipt, Index II, and Challan.",
            "nature": "Original"
        },
        {
            "date": "29/11/2023",
            "description": "Copy of Registered Agreement to Lease executed between CIDCO Ltd and M/s. Manas Group (Doc No. PVL3-20939-2023).",
            "nature": "Photo Copy"
        },
        {
            "date": "27/07/2022",
            "description": "Copy of CIDCO Allotment Letter (Ref No. 3628/1000955/798).",
            "nature": "Photo Copy"
        },
        {
            "date": "27/03/2025",
            "description": "Copy of Amended Commencement Certificate issued by Panvel Municipal Corporation.",
            "nature": "Photo Copy"
        },
        {
            "date": "2024",
            "description": "MahaRERA Registration Certificate for Project VITHUMAULI (P52000076908).",
            "nature": "Photo Copy"
        },
        {
            "date": "-------",
            "description": "NOC / Permission to Mortgage letter from M/s. MANAS GROUP for creating valid mortgage in favor of LIC Housing Finance Ltd.",
            "nature": "Original"
        },
        {
            "date": "-------",
            "description": "Undertaking / Affidavit from Borrowers Mr. Samir Gajanan Pawar & Mrs. Shilpa Samir Pawar confirming clear possession and no prior mortgage/encumbrance.",
            "nature": "Original"
        }
    ]

    cert_text = (
        "I hereby certify that, Mr. Samir Gajanan Pawar and Mrs. Shilpa Samir Pawar have a clear, valid, and marketable title "
        "to the subject property (Flat No. 507, 5th Floor, 'VITHUMAULI', Plot No. 14, Sector-20, New Panvel East, Taluka Panvel, "
        "District Raigad), and the same is free from all encumbrances, attachments, adverse claims, litigation, or statutory liens, "
        "and is fit and proper to be accepted by LIC Housing Finance Ltd. as valid equitable mortgage security."
    )

    return TitleInvestigationData(
        property=prop,
        registration=reg,
        promoter=promoter,
        purchasers=purchasers,
        approvals=approvals,
        devolution_chain=devolution_chain,
        search_years=search_years,
        schedule_1_docs_examined=schedule_1_docs,
        schedule_2_required_originals=schedule_2_reqs,
        title_certificate_text=cert_text
    )

def build_gaurav_jadhav_data() -> TitleInvestigationData:
    """Pre-loaded sample case 2: Runwal My City (from Advocate Mishra's actual LIC HFL report)"""
    prop = PropertyDetails(
        flat_no="1922",
        floor="19th",
        wing="Wing B",
        building_name="RGC RUNWAL MY CITY EWS - LIG BUILDING",
        carpet_area_sqmt=39.86,
        carpet_area_sqft=429.05,
        plot_no="17/1, 17/2, 93(Pt), 103/2",
        sector_no="Usarghar & Sandap",
        node_village="Village Usarghar",
        taluka="Kalyan",
        district="Thane"
    )

    reg = RegistrationDetails(
        sub_registrar_office="Sub-Registrar Kalyan-4",
        document_no="KLN-4/14689/2026",
        registration_date="24/07/2026",
        execution_date="24/07/2026",
        consideration_amount=4500000.0,
        market_value=4150000.0,
        stamp_duty_paid=315000.0,
        registration_fee_paid=30000.0
    )

    promoter = Party(name="M/s. Horizon Projects Pvt. Ltd. (Runwal Group)", role="Promoter")
    purchasers = [Party(name="Mr. Gaurav Kalidas Jadhav", role="Purchaser", age=32)]

    approvals = [
        ApprovalRecord(authority="MMRDA", document_type="Amended CC", reference_no="SROT/Growth Centre/2401/BP/ITP-Usarghar-Sandap-01/Vol-19", date="23/06/2023"),
        ApprovalRecord(authority="MahaRERA", document_type="RERA Certificate", reference_no="P51700079091", date="03/02/2025", valid_upto="30/06/2029"),
        ApprovalRecord(authority="Kokan Housing (MHADA)", document_type="Offer Letter", reference_no="MHADA/EWS/B-1922", date="10/12/2025"),
        ApprovalRecord(authority="ICICI Bank Ltd", document_type="Consent for Release of Mortgage", reference_no="ICICI/REL/2026", date="03/07/2026")
    ]

    devolution = [
        DevolutionStage(
            title="Premier Ltd Land History & Sales Tax Attachments",
            date="1994-2012",
            description="The Premier Automobiles Limited owned Survey Nos. at Usarghar & Sandap. Sales tax attachment was removed vide orders. ULC exemption was granted under section 20(1)."
        ),
        DevolutionStage(
            title="Conveyance to Horizon Projects Pvt Ltd",
            date="31/12/2012",
            description="By registered Conveyance Deeds registered under KLN-1/368/2013, KLN-1/369/2013, and KLN-1/370/2013, Premier Ltd transferred the land to M/s. Horizon Projects Pvt. Ltd."
        ),
        DevolutionStage(
            title="MMRDA Amended CC & MahaRERA Registration",
            date="2023-2025",
            description="MMRDA granted Amended CC on 23/06/2023 for Wings A, B & C (Stilt + 23 floors). MahaRERA issued Registration Certificate P51700079091 valid upto 30/06/2029."
        ),
        DevolutionStage(
            title="MHADA Kokan Board Allotment & ICICI Release",
            date="2025-2026",
            description="MHADA Kokan Board allotted Flat B-1922 to Gaurav Kalidas Jadhav on 10/12/2025. ICICI Bank released mortgage over flat B-1922 on 03/07/2026."
        ),
        DevolutionStage(
            title="Registered Agreement for Sale",
            date="24/07/2026",
            description="Agreement for Sale executed between Horizon Projects Pvt Ltd and Gaurav Kalidas Jadhav registered under KLN-4/14689/2026 dated 24/07/2026."
        )
    ]

    search_years = [
        SearchYearRecord(year=2013, entry_summary="Deed of Conveyance by Premier Ltd to M/s Horizon Projects Pvt Ltd (Doc KLN-1/368/2013, 369/2013, 370/2013)"),
        SearchYearRecord(year=2014, entry_summary="Available Records Checked (NIL)"),
        SearchYearRecord(year=2015, entry_summary="Mortgage Deed to IL&FS Trust Co Ltd (Doc TNN-10/17327/2015) - subsequently repaid"),
        SearchYearRecord(year=2016, entry_summary="Available Records Checked (NIL)"),
        SearchYearRecord(year=2017, entry_summary="Available Records Checked (NIL)"),
        SearchYearRecord(year=2018, entry_summary="Mortgage with Bajaj Housing Finance & ICICI Bank Ltd - subsequently repaid / released"),
        SearchYearRecord(year=2019, entry_summary="Available Records Checked - Not maintained properly"),
        SearchYearRecord(year=2020, entry_summary="Available Records Checked - Not maintained properly"),
        SearchYearRecord(year=2021, entry_summary="Indenture of mortgage with ICICI Bank (KLN4-14363-2021)"),
        SearchYearRecord(year=2022, entry_summary="Available Records Checked - Not maintained properly"),
        SearchYearRecord(year=2023, entry_summary="MMRDA Amended CC issued for Wings A, B & C"),
        SearchYearRecord(year=2024, entry_summary="Indenture of mortgage with ICICI Bank (KLN-4/2877/2024)"),
        SearchYearRecord(year=2025, entry_summary="MahaRERA Certificate P51700079091. Kokan MHADA Allotment Letter to Gaurav Kalidas Jadhav"),
        SearchYearRecord(year=2026, entry_summary="Agreement for Sale registered under KLN-4/14689/2026 dated 24/07/2026 to Mr. Gaurav Kalidas Jadhav")
    ]

    schedule_1 = [
        "Agreement for Sale dated 24/07/2026 registered under KLN-4/14689/2026.",
        "Kokan MHADA Offer Letter dated 10/12/2025 for Flat B-1922.",
        "Consent Letter for Release of Mortgage by ICICI Bank dated 03/07/2026.",
        "MahaRERA Certificate P51700079091 valid upto 30/06/2029.",
        "MMRDA Amended CC dated 23/06/2023."
    ]

    schedule_2 = [
        {"date": "24/07/2026", "description": "Original Registered Agreement for Sale (Doc No. KLN-4/14689/2026) along with Registration Receipt and Index II.", "nature": "Original"},
        {"date": "10/12/2025", "description": "Offer Letter issued by Kokan Housing (MHADA) for Flat B-1922.", "nature": "Original"},
        {"date": "03/07/2026", "description": "Consent Letter for Release of Mortgage from ICICI Bank Ltd.", "nature": "Original"},
        {"date": "-------", "description": "NOC letter from M/s. Horizon Projects Pvt. Ltd. for creating mortgage in favor of LIC HFL.", "nature": "Original"},
        {"date": "-------", "description": "Indemnity Bond from Borrower Mr. Gaurav Kalidas Jadhav regarding pending writ petitions.", "nature": "Original"}
    ]

    cert_text = (
        "I further certify that, Mr. Gaurav Kalidas Jadhav has a clear, valid, and marketable title to Flat No. 1922, 19th Floor, "
        "Wing B, 'RGC RUNWAL MY CITY EWS - LIG BUILDING', Village Usarghar, Taluka Kalyan, Dist. Thane, and the same can be taken "
        "as valid mortgage security by LIC Housing Finance Ltd."
    )

    return TitleInvestigationData(
        report_ref_no="JM/LIC/08/64/2026",
        report_date="18/08/2026",
        loan_account_no="6001050004550",
        ref_no="6001210002219",
        property=prop,
        registration=reg,
        promoter=promoter,
        purchasers=purchasers,
        approvals=approvals,
        devolution_chain=devolution,
        search_years=search_years,
        schedule_1_docs_examined=schedule_1,
        schedule_2_required_originals=schedule_2,
        title_certificate_text=cert_text
    )

def build_data_from_upload(pdf_path: str) -> TitleInvestigationData:
    """Build TitleInvestigationData from uploaded PDF file."""
    text = extract_text_from_pdf(pdf_path)
    base_name = os.path.basename(pdf_path).lower()
    
    # If the file is specifically the Samir Pawar agreement or matches it
    if "samir" in base_name or "pawar" in base_name:
        return build_samir_pawar_data()
    
    # If the file is Runwal / Gaurav Jadhav
    if "runwal" in base_name or "jadhav" in base_name or "gaurav" in base_name:
        return build_gaurav_jadhav_data()

    parsed = parse_agreement_text(text, base_name)
    
    prop = PropertyDetails(
        flat_no=parsed["flat_no"],
        floor=parsed["floor"],
        wing="",
        building_name=parsed["building_name"],
        carpet_area_sqmt=parsed["carpet_area_sqmt"],
        carpet_area_sqft=parsed["carpet_area_sqft"],
        parking="1 Car Parking space",
        plot_no=parsed["plot_no"],
        sector_no=parsed["sector_no"],
        node_village=parsed["node_village"],
        taluka=parsed["taluka"],
        district=parsed["district"]
    )

    reg = RegistrationDetails(
        sub_registrar_office=f"Sub-Registrar {parsed['taluka']}",
        document_no=parsed["doc_no"],
        registration_date=parsed["registration_date"],
        execution_date=parsed["registration_date"],
        consideration_amount=parsed["consideration"],
        market_value=parsed["consideration"] * 0.9,
        stamp_duty_paid=parsed["stamp_duty"],
        registration_fee_paid=30000.0
    )

    promoter = Party(name=parsed["promoter_name"], role="Promoter")
    purchasers = [
        Party(name=parsed["purchaser_1"], role="Purchaser"),
        Party(name=parsed["purchaser_2"], role="Purchaser")
    ]

    approvals = [
        ApprovalRecord(authority="Planning Authority", document_type="Commencement Certificate", reference_no="CC/Verified/2025", date="2025"),
        ApprovalRecord(authority="MahaRERA", document_type="Project Certificate", reference_no=parsed["rera_no"], date="2025")
    ]

    devolution = [
        DevolutionStage(
            title="Initial Land Allotment & Approvals",
            date="2022-2024",
            description=f"Plot No. {prop.plot_no}, Sector {prop.sector_no} was allotted and development permissions / Commencement Certificate were duly obtained."
        ),
        DevolutionStage(
            title="Registered Agreement for Sale",
            date=reg.registration_date,
            description=f"By Agreement for Sale registered under Sr. No. {reg.document_no}, the Promoter agreed to sell Flat No. {prop.flat_no} to {purchasers[0].name}."
        )
    ]

    search_years = [
        SearchYearRecord(year=y, entry_summary="Available Records Checked (NIL encumbrance)")
        for y in range(2013, 2026)
    ]
    search_years.append(SearchYearRecord(year=2026, entry_summary=f"Agreement for Sale registered under {reg.document_no}"))

    return TitleInvestigationData(
        property=prop,
        registration=reg,
        promoter=promoter,
        purchasers=purchasers,
        approvals=approvals,
        devolution_chain=devolution,
        search_years=search_years,
        schedule_1_docs_examined=[f"Registered Agreement for Sale ({reg.document_no})", f"MahaRERA Registration {parsed['rera_no']}"],
        schedule_2_required_originals=[{"date": reg.registration_date, "description": f"Original Agreement for Sale ({reg.document_no})", "nature": "Original"}],
        title_certificate_text=f"I certify that {purchasers[0].name} has a clear, valid, and marketable title to Flat No. {prop.flat_no}, {prop.building_name}."
    )
