"""
Bank-Standard Title Investigation Report (.docx) Generator
Generates full legal Title Investigation Reports matching JM Associates Advocates / LIC Housing Finance format.
"""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from core.models import TitleInvestigationData

def set_cell_border(cell, **kwargs):
    """
    Set cell borders: top, bottom, left, right.
    kwargs: color, sz, val
    """
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = tcPr.first_child_found_in("w:tcBorders")
    if tcBorders is None:
        tcBorders = OxmlElement('w:tcBorders')
        tcPr.append(tcBorders)
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = 'w:{}'.format(edge)
            element = tcBorders.find(qn(tag))
            if element is None:
                element = OxmlElement(tag)
                tcBorders.append(element)
            for key, val in edge_data.items():
                element.set(qn('w:{}'.format(key)), str(val))

def set_cell_shading(cell, color_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def generate_title_report_docx(data: TitleInvestigationData, output_path: str) -> str:
    doc = Document()
    
    # Page setup - Standard Letter / A4 with 0.8 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Styles
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(11)
    font.color.rgb = RGBColor(30, 30, 30)

    # 1. Header Block (Advocate Letterhead)
    header_p = doc.add_paragraph()
    header_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_firm = header_p.add_run("JM ASSOCIATES\n")
    run_firm.bold = True
    run_firm.font.size = Pt(18)
    run_firm.font.color.rgb = RGBColor(16, 44, 87)
    
    run_sub = header_p.add_run("ADVOCATES & LEGAL CONSULTANTS\n")
    run_sub.bold = True
    run_sub.font.size = Pt(11)
    run_sub.font.color.rgb = RGBColor(80, 80, 80)
    
    run_adv = header_p.add_run(f"{data.advocate_name}\n")
    run_adv.bold = True
    run_adv.font.size = Pt(10)
    
    run_contact = header_p.add_run(f"{data.advocate_details}\n")
    run_contact.font.size = Pt(9)
    run_contact.font.italic = True
    
    # Horizontal Divider Line
    div_p = doc.add_paragraph()
    div_p.paragraph_format.space_before = Pt(2)
    div_p.paragraph_format.space_after = Pt(12)
    div_run = div_p.add_run("―" * 58)
    div_run.font.color.rgb = RGBColor(150, 150, 150)
    div_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Reference & Date Table
    meta_table = doc.add_table(rows=1, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.autofit = False
    meta_table.columns[0].width = Inches(3.5)
    meta_table.columns[1].width = Inches(3.2)
    
    p_left = meta_table.cell(0, 0).paragraphs[0]
    p_left.add_run(f"Ref:- {data.report_ref_no}").bold = True
    p_right = meta_table.cell(0, 1).paragraphs[0]
    p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_right.add_run(f"Date:- {data.report_date}").bold = True

    # Title Banner
    banner_p = doc.add_paragraph()
    banner_p.paragraph_format.space_before = Pt(14)
    banner_p.paragraph_format.space_after = Pt(14)
    banner_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    banner_run = banner_p.add_run("TITLE INVESTIGATION REPORT")
    banner_run.bold = True
    banner_run.font.size = Pt(15)
    banner_run.font.underline = True
    banner_run.font.color.rgb = RGBColor(16, 44, 87)

    # Addressee Block
    addr_p = doc.add_paragraph()
    addr_p.paragraph_format.space_after = Pt(10)
    addr_p.paragraph_format.line_spacing = 1.15
    addr_p.add_run("To,\n").bold = True
    addr_p.add_run(f"The Area Manager,\n{data.bank_name}\n{data.bank_branch}\n\nDear Sir/Madam,\n")
    addr_p.add_run(f"Ref No.: {data.ref_no}\n")
    addr_p.add_run(f"Title Reference Loan Account Number: {data.loan_account_no}\n").bold = True

    # Applicant Name
    purchaser_names = " & ".join([p.name.upper() for p in data.purchasers])
    app_p = doc.add_paragraph()
    app_p.paragraph_format.space_after = Pt(10)
    app_p.add_run("NAME OF THE APPLICANT(S):\t").bold = True
    app_p.add_run(f"{purchaser_names}\n").bold = True

    # Subject Property Reference
    subj_p = doc.add_paragraph()
    subj_p.paragraph_format.space_after = Pt(12)
    subj_p.paragraph_format.line_spacing = 1.15
    subj_p.add_run("Ref: Title Report in respect of ").bold = True
    
    prop = data.property
    prop_desc_text = (
        f"Flat No. {prop.flat_no}, on {prop.floor} Floor, (Admeasuring {prop.carpet_area_sqmt:.3f} Sq. Mtrs. "
        f"/ {prop.carpet_area_sqmt * 10.7639:.2f} Sq. Ft.) {f'in Wing {prop.wing}, ' if prop.wing else ''}"
        f"in the Building known as “{prop.building_name.upper()}” constructed on Plot No. {prop.plot_no}, "
        f"Sector No. {prop.sector_no}, at {prop.node_village}, Taluka {prop.taluka} & District {prop.district}."
    )
    subj_p.add_run(prop_desc_text)

    # 1. DESCRIPTION OF IMMOVABLE PROPERTY
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(12)
    h1.add_run("1. DESCRIPTION OF IMMOVABLE PROPERTY:").bold = True
    p1 = doc.add_paragraph(prop_desc_text)
    p1.paragraph_format.line_spacing = 1.15
    
    if prop.boundaries:
        bp = doc.add_paragraph()
        bp.add_run("Boundaries of the Plot:\n").bold = True
        for side, bnd in prop.boundaries.items():
            bp.add_run(f"  • {side}: {bnd}\n")

    # 2. DEVOLUTION OF TITLE
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(12)
    h2.add_run("2. DEVOLUTION OF TITLE (LAND & FLAT HISTORY):").bold = True
    
    intro_dev = doc.add_paragraph("We have perused the documents forwarded to us and found that:")
    intro_dev.paragraph_format.space_after = Pt(6)

    for stage in data.devolution_chain:
        sp = doc.add_paragraph()
        sp.paragraph_format.line_spacing = 1.15
        sp.paragraph_format.space_after = Pt(8)
        run_obs = sp.add_run("Further it is observed that, ")
        run_obs.bold = True
        sp.add_run(stage.description)

    # 3. MINOR INTEREST
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(10)
    h3.add_run("3. MINOR INTEREST:").bold = True
    doc.add_paragraph("As per documents forwarded to us, we find that minor interest is not involved.")

    # 4. POSSESSION
    h4 = doc.add_paragraph()
    h4.paragraph_format.space_before = Pt(10)
    h4.add_run("4. POSSESSION:").bold = True
    doc.add_paragraph("Property under construction / possession handed over as per terms of registered Agreement for Sale. It is advisable to make physical verification of the property for ascertaining possession.")

    # 5. APPLICABILITY OF ULC ACT
    h5 = doc.add_paragraph()
    h5.paragraph_format.space_before = Pt(10)
    h5.add_run("5. APPLICABILITY OF THE URBAN LAND (CEILING AND REGULATION) ACT, 1976:").bold = True
    doc.add_paragraph("N.A. / Cleared as per applicable CIDCO and Urban Development Department regulations.")

    # 6. SEARCHES
    h6 = doc.add_paragraph()
    h6.paragraph_format.space_before = Pt(10)
    h6.add_run("6. SEARCHES:").bold = True
    p_srch = doc.add_paragraph(
        f"We have taken e-search for the above referred property in the Official IGR Website of the Government "
        f"of Maharashtra for the period of 13 years i.e. from 2013 to 2026 and on perusal of the information/papers "
        f"and records made available to us, it is observed that there are no adverse charges/mortgages registered "
        f"against the said subject flat, except permitted developer charges if any released prior to execution."
    )
    p_srch.paragraph_format.line_spacing = 1.15

    # 7. CERTIFICATE
    h7 = doc.add_paragraph()
    h7.paragraph_format.space_before = Pt(12)
    h7.add_run("7. CERTIFICATE OF TITLE:").bold = True
    
    cert_box = doc.add_paragraph()
    cert_box.paragraph_format.space_before = Pt(6)
    cert_box.paragraph_format.space_after = Pt(12)
    cert_box.paragraph_format.line_spacing = 1.2
    c_run = cert_box.add_run(data.title_certificate_text)
    c_run.bold = True
    c_run.font.color.rgb = RGBColor(16, 44, 87)

    # SCHEDULE-I: DOCUMENTS EXAMINED
    doc.add_page_break()
    h_s1 = doc.add_paragraph()
    h_s1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h_s1.add_run("SCHEDULE - I\n").bold = True
    h_s1.add_run("DOCUMENTS EXAMINED BY ADVOCATE (COPIES)").bold = True
    
    for idx, doc_item in enumerate(data.schedule_1_docs_examined, 1):
        dp = doc.add_paragraph()
        dp.paragraph_format.space_after = Pt(4)
        dp.add_run(f"{idx}. {doc_item}")

    # SCHEDULE-II: REQUIRED ORIGINAL DOCUMENTS
    doc.add_paragraph()
    h_s2 = doc.add_paragraph()
    h_s2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h_s2.add_run("SCHEDULE - II\n").bold = True
    h_s2.add_run("REQUIRED ORIGINAL DOCUMENTS TO BE COLLECTED PRIOR TO MORTGAGE").bold = True

    # Table for Schedule II
    t_s2 = doc.add_table(rows=1, cols=4)
    t_s2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_s2.autofit = False
    
    widths = [Inches(0.6), Inches(1.2), Inches(3.8), Inches(1.2)]
    headers = ["Sr", "Date", "Document Description", "Nature"]
    
    hdr_cells = t_s2.rows[0].cells
    for i, h_text in enumerate(headers):
        hdr_cells[i].text = h_text
        hdr_cells[i].paragraphs[0].runs[0].bold = True
        hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_shading(hdr_cells[i], "D9E1F2")
        hdr_cells[i].width = widths[i]
        
    for idx, row_item in enumerate(data.schedule_2_required_originals, 1):
        row_cells = t_s2.add_row().cells
        row_cells[0].text = str(idx)
        row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[1].text = row_item.get("date", "-------")
        row_cells[2].text = row_item.get("description", "")
        row_cells[3].text = row_item.get("nature", "Original")
        row_cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        for c_idx, cell in enumerate(row_cells):
            cell.width = widths[c_idx]
            set_cell_border(cell,
                            top={'val': 'single', 'sz': 4, 'color': 'BFBFBF'},
                            bottom={'val': 'single', 'sz': 4, 'color': 'BFBFBF'},
                            left={'val': 'single', 'sz': 4, 'color': 'BFBFBF'},
                            right={'val': 'single', 'sz': 4, 'color': 'BFBFBF'})

    # 13-YEAR SEARCH REPORT TABLE
    doc.add_page_break()
    h_srch = doc.add_paragraph()
    h_srch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h_srch.add_run("S E A R C H   R E P O R T\n").bold = True
    
    srch_sub = doc.add_paragraph()
    srch_sub.paragraph_format.line_spacing = 1.15
    srch_sub.add_run(f"PROPERTY: {prop_desc_text}\n").bold = True
    srch_sub.add_run(f"OWNER(S): {purchaser_names}\n").bold = True
    srch_sub.add_run(
        f"THIS IS TO CERTIFY THAT I have taken search in respect of the above said property for the "
        f"period of 13 years from 2013 to 2026 in the Office of Sub-Registrar Panvel which is as follows: -"
    )

    # Search Table
    t_srch = doc.add_table(rows=1, cols=2)
    t_srch.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_srch.autofit = False
    
    srch_widths = [Inches(1.2), Inches(5.6)]
    hdr_srch = t_srch.rows[0].cells
    hdr_srch[0].text = "YEARS"
    hdr_srch[0].paragraphs[0].runs[0].bold = True
    hdr_srch[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    hdr_srch[0].width = srch_widths[0]
    set_cell_shading(hdr_srch[0], "D9E1F2")
    
    hdr_srch[1].text = "PARTICULARS OF TRANSACTIONS REGISTERED"
    hdr_srch[1].paragraphs[0].runs[0].bold = True
    hdr_srch[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    hdr_srch[1].width = srch_widths[1]
    set_cell_shading(hdr_srch[1], "D9E1F2")

    for rec in data.search_years:
        row = t_srch.add_row().cells
        row[0].text = str(rec.year)
        row[0].paragraphs[0].runs[0].bold = True
        row[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row[0].width = srch_widths[0]
        
        row[1].text = rec.entry_summary
        row[1].width = srch_widths[1]
        for cell in row:
            set_cell_border(cell,
                            top={'val': 'single', 'sz': 4, 'color': 'BFBFBF'},
                            bottom={'val': 'single', 'sz': 4, 'color': 'BFBFBF'},
                            left={'val': 'single', 'sz': 4, 'color': 'BFBFBF'},
                            right={'val': 'single', 'sz': 4, 'color': 'BFBFBF'})

    # Signature Block
    sig_p = doc.add_paragraph()
    sig_p.paragraph_format.space_before = Pt(24)
    sig_p.paragraph_format.line_spacing = 1.15
    sig_p.add_run(f"Place: Navi Mumbai\nDate: {data.report_date}\n\n")
    sig_p.add_run(f"For JM Associates Advocates\n\n\n\n").bold = True
    sig_p.add_run(f"{data.advocate_name}\nAdvocate High Court").bold = True

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path
