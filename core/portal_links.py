"""
Maharashtra Property & Land Record Search Portals Link Generator
"""

def get_portal_directories():
    return {
        "Property Registration & IGR": [
            {
                "name": "Free Search (Index II, basic data)",
                "url": "https://freesearchigrservice.maharashtra.gov.in/",
                "description": "Free public search for registered deeds and Index II across Maharashtra."
            },
            {
                "name": "Paid Detailed Search (e-Search)",
                "url": "https://esearchigr.maharashtra.gov.in/portal/esearchlogin.aspx",
                "description": "Detailed IGR search with GRAS challan support and complete index download."
            },
            {
                "name": "Notice of Intimation (NOI Filing)",
                "url": "https://efilingigr.maharashtra.gov.in/efiling/frmPropertyDetails.aspx",
                "description": "Search registered Bank Loan Mortgage Notices / Charges on property."
            }
        ],
        "RERA Verification": [
            {
                "name": "MahaRERA Project Search",
                "url": "https://maharera.maharashtra.gov.in/",
                "description": "Verify Project Registration Certificate, CC, OC, valid upto date, and litigations."
            }
        ],
        "Land Records (7/12, Property Card, Satbara)": [
            {
                "name": "7/12 Extract & Property Card (Free)",
                "url": "https://bhulekh.mahabhumi.gov.in/",
                "description": "Free view of land records, 7/12 extract, and urban property cards."
            },
            {
                "name": "Paid Digitally Signed 7/12",
                "url": "https://digitalsatbara.mahabhumi.gov.in/dslr",
                "description": "Official digitally signed 7/12 extract from Revenue Department."
            },
            {
                "name": "Property Card Download",
                "url": "https://bhumiabhilekh.maharashtra.gov.in/Services/PropertyCardDownload",
                "description": "Official City Survey / Akhiv Patrika download."
            },
            {
                "name": "Mutation Status (Ferfar)",
                "url": "https://digitalsatbara.mahabhumi.gov.in/pc_status#",
                "description": "Check pending and approved land mutation (फेरफार) status."
            },
            {
                "name": "Aaplichawdi (Digital Notice Board)",
                "url": "https://digitalsatbara.mahabhumi.gov.in/aaplichawdi",
                "description": "Digital notice board for public notices of land mutation entries."
            },
            {
                "name": "CTS from Survey Number",
                "url": "https://digitalsatbara.mahabhumi.gov.in/section12",
                "description": "Conversion and linking between Survey Number and CTS Number."
            }
        ],
        "Mapping & Location": [
            {
                "name": "Land Map (Mahabhunakasha Cadastral)",
                "url": "https://mahabhunakasha.mahabhumi.gov.in/27/index.html",
                "description": "GIS cadastral village maps and plot boundaries."
            }
        ],
        "Court Case Status (Title Litigation Check)": [
            {
                "name": "All District Courts (eCourts India)",
                "url": "https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/index",
                "description": "Search civil/commercial disputes against owner/builder in District Courts."
            },
            {
                "name": "Bombay High Court Case Status",
                "url": "https://bombayhighcourt.gov.in/bhc/casestatus/casenumber",
                "description": "Search Writ Petitions, Appeals, and Special Civil Suits in Bombay High Court."
            },
            {
                "name": "Land-related Case Tracking (eCourt Mahabhumi)",
                "url": "https://mahabhumi.gov.in/mahabhumilink/eCourt/eCourt",
                "description": "Direct tracking of land revenue disputes and revenue court appeals."
            }
        ],
        "Building Permissions & Authorities": [
            {
                "name": "CIDCO Allotment Letter Verification",
                "url": "https://cidcohomes.com/payment-installment/",
                "description": "Verify CIDCO plot/flat allotment and payment status."
            },
            {
                "name": "CIDCO COPAS Building Approval Search",
                "url": "http://202.191.151.14/BpamsClient/CitizenSearch/CitizenSearch.aspx?sOrgName=CIDCO",
                "description": "CIDCO BPAMS building plan approvals and Commencement Certificates."
            },
            {
                "name": "NAINA Portal (CIDCO)",
                "url": "https://cidco.maharashtra.gov.in/Page?Token=7788D6B3375",
                "description": "Navi Mumbai Airport Influence Notified Area permissions."
            },
            {
                "name": "Panvel Municipal Corporation Town Planning",
                "url": "https://panvelcorporation.maharashtra.gov.in/town_planning_department",
                "description": "Panvel Municipal Corporation CC, OC, and town planning records."
            },
            {
                "name": "Maharashtra BPAMS (MahaVastu)",
                "url": "https://mahavastu.maharashtra.gov.in/",
                "description": "Centralized Maharashtra Building Plan Approval System."
            },
            {
                "name": "MHADA Approvals & Lotteries",
                "url": "https://maps.mhada.gov.in/Bpamsclient/CitizenSearch/CitizenSearch.aspx",
                "description": "MHADA building permissions and draw allotment results."
            },
            {
                "name": "Environment Clearance Portal (Parivesh)",
                "url": "https://environmentclearance.nic.in/",
                "description": "State and Central environmental clearances for large projects."
            },
            {
                "name": "GRAS Challan Verification",
                "url": "https://gras.mahakosh.gov.in/",
                "description": "Verify Government Receipt Accounting System challans (Stamp Duty/Search)."
            }
        ]
    }
