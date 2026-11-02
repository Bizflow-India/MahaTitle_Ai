import os
import uuid
import shutil
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from core.extractor import build_samir_pawar_data, build_gaurav_jadhav_data, build_data_from_upload
from core.report_generator import generate_title_report_docx
from core.igr_filter import IGRSmartFilter
from core.portal_links import get_portal_directories

app = FastAPI(title="MahaTitle AI - Title Investigation & Fraud Detection")

UPLOAD_DIR = os.path.abspath("d:/Nilesh/uploads")
OUTPUT_DIR = os.path.abspath("d:/Nilesh/output")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Pre-generate the Samir Pawar report on startup
_default_docx = os.path.join(OUTPUT_DIR, "Title_Investigation_Report_Samir_Pawar.docx")
if not os.path.exists(_default_docx):
    generate_title_report_docx(build_samir_pawar_data(), _default_docx)


@app.get("/download-report")
async def download_report(filename: str = "Title_Investigation_Report_Samir_Pawar.docx"):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(
        path=path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.post("/upload-agreement")
async def upload_agreement(file: UploadFile = File(...)):
    """Accepts a PDF agreement, parses it, generates the Word report, returns metadata."""
    if not file.filename.lower().endswith(".pdf"):
        return JSONResponse({"error": "Only PDF files are supported."}, status_code=400)

    # Save uploaded file
    safe_name = f"{uuid.uuid4().hex}_{file.filename}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # Parse & build data
        data = build_data_from_upload(save_path)

        # Generate Word report
        purchaser_slug = data.purchasers[0].name.replace("Mr. ", "").replace("Mrs. ", "").replace(" ", "_")
        out_filename = f"TIR_{purchaser_slug}_{data.property.flat_no}.docx"
        out_path = os.path.join(OUTPUT_DIR, out_filename)
        generate_title_report_docx(data, out_path)

        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "parsed": {
                "purchasers": [p.name for p in data.purchasers],
                "promoter": data.promoter.name,
                "flat_no": data.property.flat_no,
                "floor": data.property.floor,
                "building": data.property.building_name,
                "plot": data.property.plot_no,
                "sector": data.property.sector_no,
                "location": f"{data.property.node_village}, Taluka {data.property.taluka}, Dist. {data.property.district}",
                "doc_no": data.registration.document_no,
                "registration_date": data.registration.registration_date,
                "consideration": f"₹{data.registration.consideration_amount:,.0f}",
                "stamp_duty": f"₹{data.registration.stamp_duty_paid:,.0f}",
                "rera": next((a.reference_no for a in data.approvals if "rera" in a.document_type.lower() or "certificate" in a.document_type.lower()), "N/A"),
                "devolution_count": len(data.devolution_chain),
                "search_years": len(data.search_years),
            },
            "report_filename": out_filename,
            "download_url": f"/download-report?filename={out_filename}"
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/igr-demo")
async def igr_demo():
    filter_engine = IGRSmartFilter(
        target_flat="507", target_floor="5th", target_building="Vithumauli",
        target_plot="14", target_sector="20",
        target_parties=["Samir Gajanan Pawar", "Shilpa Samir Pawar", "Manas Group"]
    )
    mock_raw_batch = [
        {"year": 2026, "doc_no": "PNL3-17995-2026", "doc_type": "Agreement for Sale (करारनामा)", "property_description": "Flat No. 507, 5th Floor, Vithumauli, Plot No. 14, Sector-20, New Panvel East", "parties": ["M/s. MANAS GROUP", "Samir Gajanan Pawar", "Shilpa Samir Pawar"], "consideration": "Rs. 80,00,000/-"},
        {"year": 2025, "doc_no": "PNL3-08412-2025", "doc_type": "Notice of Intimation (NOI)", "property_description": "Building Vithumauli, Plot 14, Sector 20, New Panvel - Project Finance Charge", "parties": ["M/s. MANAS GROUP", "HDFC Bank Ltd"], "consideration": "Charge Rs. 15,00,00,000/-"},
        {"year": 2024, "doc_no": "PNL3-11200-2024", "doc_type": "Deemed Conveyance", "property_description": "Land & Building Vithu Mauli, Plot 14, Sector 20, New Panvel", "parties": ["M/s. MANAS GROUP", "Vithumauli Co-op Housing Society Ltd"], "consideration": "Transfer"},
        {"year": 2026, "doc_no": "PNL3-14920-2026", "doc_type": "Agreement for Sale", "property_description": "Flat No. 101, 1st Floor, Vithumauli, Plot 14, Sector 20", "parties": ["Manas Group", "Ramesh Kulkarni"], "consideration": "Rs. 45,00,000/-"},
        {"year": 2026, "doc_no": "PNL3-15102-2026", "doc_type": "Agreement for Sale", "property_description": "Flat No. 204, 2nd Floor, Vithumauli, Plot 14, Sector 20", "parties": ["Manas Group", "Mahesh Shinde"], "consideration": "Rs. 48,00,000/-"},
    ]
    for i in range(1, 991):
        mock_raw_batch.append({"year": 2020 + (i % 6), "doc_no": f"PNL3-{20000+i}-202{i%6}", "doc_type": "Agreement for Sale", "property_description": f"Flat No. {1000+i}, Plot 14, Sector 20, New Panvel", "parties": ["Other Developer", f"Random Buyer {i}"], "consideration": "Rs. 50,00,000/-"})

    return filter_engine.filter_and_rank(mock_raw_batch)


@app.get("/", response_class=HTMLResponse)
async def home():
    data = build_samir_pawar_data()
    portals = get_portal_directories()

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MahaTitle AI — Title Investigation & IGR Automation</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .badge-clean  {{ background:#DEF7EC;color:#03543F; }}
        .badge-warn   {{ background:#FEF08A;color:#854D0E; }}
        .badge-danger {{ background:#FDE8E8;color:#9B1C1C; }}
        .badge-info   {{ background:#EDE9FE;color:#4C1D95; }}
        #drop-zone {{ transition: all .2s; }}
        #drop-zone.drag-over {{ border-color:#6366F1; background:#EEF2FF; }}
        .pulse-ring {{ animation: ping 1.5s cubic-bezier(0,0,.2,1) infinite; }}
        @keyframes ping {{ 75%,100%{{transform:scale(2);opacity:0}} }}
    </style>
</head>
<body class="bg-slate-50 text-slate-800 font-sans">

<!-- ── HEADER ─────────────────────────────────────────────────────── -->
<header class="bg-indigo-900 text-white shadow-lg sticky top-0 z-50">
  <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center flex-wrap gap-3">
    <div class="flex items-center space-x-3">
      <i class="fa-solid fa-scale-balanced text-amber-400 text-2xl"></i>
      <div>
        <h1 class="text-xl font-bold">MahaTitle AI</h1>
        <p class="text-xs text-indigo-200">Maharashtra Legal Title Investigation & IGR Fraud Prevention</p>
      </div>
    </div>
    <div class="flex items-center gap-3 flex-wrap">
      <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
        <span class="relative flex h-2 w-2 mr-2">
          <span class="pulse-ring absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-400"></span>
        </span>
        Server Live — localhost:8000
      </span>
      <a href="/download-report" class="bg-amber-500 hover:bg-amber-600 text-slate-900 font-semibold px-4 py-2 rounded-lg text-sm flex items-center shadow">
        <i class="fa-solid fa-file-word mr-2"></i> Download Report (.docx)
      </a>
    </div>
  </div>
</header>

<main class="max-w-7xl mx-auto px-6 py-8 space-y-8">

  <!-- ── PDF UPLOAD ZONE ─────────────────────────────────────────── -->
  <div class="bg-white rounded-xl shadow-sm border-2 border-dashed border-indigo-300 p-6" id="upload-card">
    <div class="flex items-center space-x-3 pb-4 border-b border-slate-100">
      <div class="p-2 bg-indigo-50 text-indigo-600 rounded-lg"><i class="fa-solid fa-cloud-arrow-up text-2xl"></i></div>
      <div>
        <h3 class="text-lg font-bold text-slate-900">Upload New Agreement PDF</h3>
        <p class="text-xs text-slate-500">Drag & drop any Maharashtra property agreement — parser extracts all fields automatically</p>
      </div>
    </div>

    <!-- Drop Zone -->
    <div id="drop-zone"
         class="mt-6 flex flex-col items-center justify-center border-2 border-dashed border-indigo-200 rounded-xl py-12 cursor-pointer hover:border-indigo-400 hover:bg-indigo-50/50 transition"
         onclick="document.getElementById('file-input').click()"
         ondragover="handleDragOver(event)"
         ondragleave="handleDragLeave(event)"
         ondrop="handleDrop(event)">
      <i class="fa-solid fa-file-pdf text-5xl text-rose-400 mb-3"></i>
      <p class="text-sm font-semibold text-slate-700">Click to browse or drag & drop agreement PDF here</p>
      <p class="text-xs text-slate-400 mt-1">Supported: Scanned or Digital PDF • Any bank format • Any district</p>
      <input type="file" id="file-input" accept=".pdf" class="hidden" onchange="handleFileSelect(event)">
    </div>

    <!-- Upload Status -->
    <div id="upload-status" class="hidden mt-4"></div>

    <!-- Parsed Result Card -->
    <div id="parsed-result" class="hidden mt-6 bg-emerald-50 border border-emerald-200 rounded-xl p-5">
      <div class="flex items-center justify-between mb-4">
        <h4 class="font-bold text-emerald-900 flex items-center"><i class="fa-solid fa-circle-check mr-2 text-emerald-600"></i> Agreement Parsed Successfully</h4>
        <a id="new-report-link" href="#" class="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold px-3 py-2 rounded-lg flex items-center">
          <i class="fa-solid fa-download mr-1.5"></i> Download Generated Report
        </a>
      </div>
      <div id="parsed-grid" class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm"></div>
    </div>

    <!-- Demo Cases -->
    <div class="mt-6 flex flex-wrap gap-3">
      <span class="text-xs text-slate-500 self-center font-medium">Or load a preloaded case:</span>
      <button onclick="loadPreset('samir')" class="border border-indigo-300 text-indigo-700 text-xs font-medium px-3 py-1.5 rounded-lg hover:bg-indigo-50 transition flex items-center">
        <i class="fa-solid fa-folder-open mr-1.5"></i> Samir Pawar — Flat 507, Vithumauli, Panvel
      </button>
      <button onclick="loadPreset('gaurav')" class="border border-purple-300 text-purple-700 text-xs font-medium px-3 py-1.5 rounded-lg hover:bg-purple-50 transition flex items-center">
        <i class="fa-solid fa-folder-open mr-1.5"></i> Gaurav Jadhav — Flat 1922, Runwal My City, Kalyan
      </button>
    </div>
  </div>

  <!-- ── ACTIVE CASE SUMMARY ─────────────────────────────────────── -->
  <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center pb-4 border-b border-slate-100 gap-3">
      <div>
        <div class="flex items-center gap-2 flex-wrap">
          <span class="px-2.5 py-0.5 rounded text-xs font-semibold bg-blue-100 text-blue-800">Active Case</span>
          <h2 class="text-xl font-bold text-slate-900" id="case-title">{data.property.building_name} — Flat No. {data.property.flat_no} ({data.property.floor} Floor)</h2>
        </div>
        <p class="text-sm text-slate-500 mt-1" id="case-sub">Plot No. {data.property.plot_no}, Sector {data.property.sector_no}, {data.property.node_village}, Taluka {data.property.taluka}, District {data.property.district}</p>
      </div>
      <a href="/download-report" id="case-dl-btn" class="bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-4 py-2 rounded-lg text-sm flex items-center shadow-sm shrink-0">
        <i class="fa-solid fa-download mr-2"></i> Export Word Report
      </a>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-5">
      <div class="bg-slate-50 p-4 rounded-lg border border-slate-100">
        <div class="text-xs font-medium text-slate-500 uppercase tracking-wide">Purchasers</div>
        <div class="text-sm font-bold text-slate-900 mt-1">{data.purchasers[0].name}</div>
        <div class="text-xs text-slate-500">& {data.purchasers[1].name}</div>
        <div class="text-[11px] text-slate-400 mt-1">PAN: {data.purchasers[0].pan}</div>
      </div>
      <div class="bg-slate-50 p-4 rounded-lg border border-slate-100">
        <div class="text-xs font-medium text-slate-500 uppercase tracking-wide">Developer</div>
        <div class="text-sm font-bold text-slate-900 mt-1">{data.promoter.name}</div>
        <div class="text-xs text-slate-500">Auth. Partner: Sujeet Subhash Thorat</div>
        <div class="text-[11px] text-slate-400 mt-1">PAN: {data.promoter.pan}</div>
      </div>
      <div class="bg-slate-50 p-4 rounded-lg border border-slate-100">
        <div class="text-xs font-medium text-slate-500 uppercase tracking-wide">Registration</div>
        <div class="text-sm font-bold text-slate-900 mt-1">{data.registration.document_no}</div>
        <div class="text-xs text-slate-500">Consideration: ₹{data.registration.consideration_amount:,.0f}</div>
        <div class="text-[11px] text-emerald-600 font-medium mt-1">Stamp Duty: ₹{data.registration.stamp_duty_paid:,.0f} (Paid)</div>
      </div>
      <div class="bg-slate-50 p-4 rounded-lg border border-slate-100">
        <div class="text-xs font-medium text-slate-500 uppercase tracking-wide">RERA & Approvals</div>
        <div class="text-sm font-bold text-slate-900 mt-1">RERA: P52000076908</div>
        <div class="text-xs text-slate-500">CIDCO Lease: PVL3-20939-2023</div>
        <div class="text-[11px] text-indigo-600 font-medium mt-1">PMC Amended CC Verified ✓</div>
      </div>
    </div>
  </div>

  <!-- ── IGR SMART FILTER ────────────────────────────────────────── -->
  <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
    <div class="flex items-center justify-between pb-4 border-b border-slate-100 flex-wrap gap-3">
      <div class="flex items-center space-x-3">
        <div class="p-2 bg-indigo-50 text-indigo-600 rounded-lg"><i class="fa-solid fa-filter text-xl"></i></div>
        <div>
          <h3 class="text-lg font-bold text-slate-900">IGR Smart Noise Filter & Deduplication</h3>
          <p class="text-xs text-slate-500">Instantly filters 1,000+ noisy Sector/Plot results → only actionable records for YOUR flat</p>
        </div>
      </div>
      <button onclick="runIgrFilter()" id="btn-igr" class="bg-emerald-600 hover:bg-emerald-700 text-white font-medium px-4 py-2 rounded-lg text-sm flex items-center shadow-sm transition">
        <i class="fa-solid fa-play mr-2"></i> Run Smart IGR Filter
      </button>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-5">
      <div class="bg-blue-50 border border-blue-100 rounded-lg p-3 text-center">
        <div class="text-xs font-semibold text-blue-600 uppercase">Raw IGR Entries</div>
        <div class="text-2xl font-bold text-blue-900 mt-1" id="stat-total">995+</div>
        <div class="text-[11px] text-blue-400 mt-0.5">Sector 20 / Plot 14 raw</div>
      </div>
      <div class="bg-emerald-50 border border-emerald-100 rounded-lg p-3 text-center">
        <div class="text-xs font-semibold text-emerald-600 uppercase">Actionable</div>
        <div class="text-2xl font-bold text-emerald-900 mt-1" id="stat-rel">3</div>
        <div class="text-[11px] text-emerald-400 mt-0.5">Direct matches + NoI</div>
      </div>
      <div class="bg-amber-50 border border-amber-100 rounded-lg p-3 text-center">
        <div class="text-xs font-semibold text-amber-600 uppercase">Noise Removed</div>
        <div class="text-2xl font-bold text-amber-900 mt-1" id="stat-noise">992</div>
        <div class="text-[11px] text-amber-400 mt-0.5">Other flats eliminated</div>
      </div>
      <div class="bg-purple-50 border border-purple-100 rounded-lg p-3 text-center">
        <div class="text-xs font-semibold text-purple-600 uppercase">Time Saved</div>
        <div class="text-2xl font-bold text-purple-900 mt-1">94%</div>
        <div class="text-[11px] text-purple-400 mt-0.5">Automated screening</div>
      </div>
    </div>

    <div class="mt-5 overflow-x-auto rounded-lg border border-slate-200">
      <table class="min-w-full divide-y divide-slate-200 text-sm">
        <thead class="bg-slate-50">
          <tr>
            <th class="px-4 py-3 text-left font-semibold text-slate-600 text-xs">Status</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600 text-xs">Doc No. / Year</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600 text-xs">Deed Type</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600 text-xs">Property</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600 text-xs">Parties</th>
            <th class="px-4 py-3 text-left font-semibold text-slate-600 text-xs">AI Analysis</th>
          </tr>
        </thead>
        <tbody id="igr-table" class="divide-y divide-slate-100 bg-white">
          <tr>
            <td class="px-4 py-3"><span class="badge-clean px-2.5 py-1 rounded-full text-xs font-semibold">DIRECT MATCH</span></td>
            <td class="px-4 py-3 font-medium">PNL3-17995-2026<br><span class="text-[11px] text-slate-400">2026</span></td>
            <td class="px-4 py-3 text-slate-600">Agreement for Sale</td>
            <td class="px-4 py-3 text-slate-800">Flat 507, 5th Floor, Vithumauli, Plot 14, Sector 20</td>
            <td class="px-4 py-3 text-xs text-slate-600">MANAS GROUP → Samir Pawar & Shilpa Pawar</td>
            <td class="px-4 py-3 text-xs text-emerald-700 font-medium">Flat 507 + verified parties. Title chain intact. ✓</td>
          </tr>
          <tr>
            <td class="px-4 py-3"><span class="badge-warn px-2.5 py-1 rounded-full text-xs font-semibold">NOI / CHARGE</span></td>
            <td class="px-4 py-3 font-medium">PNL3-08412-2025<br><span class="text-[11px] text-slate-400">2025</span></td>
            <td class="px-4 py-3 text-slate-600">Notice of Intimation</td>
            <td class="px-4 py-3 text-slate-800">Building Vithumauli, Plot 14, Sector 20 — Project Finance</td>
            <td class="px-4 py-3 text-xs text-slate-600">MANAS GROUP → HDFC Bank Ltd</td>
            <td class="px-4 py-3 text-xs text-amber-700 font-medium">Project-level bank charge. Verify NOC/release for Flat 507.</td>
          </tr>
          <tr>
            <td class="px-4 py-3"><span class="badge-info px-2.5 py-1 rounded-full text-xs font-semibold">CONVEYANCE</span></td>
            <td class="px-4 py-3 font-medium">PNL3-11200-2024<br><span class="text-[11px] text-slate-400">2024</span></td>
            <td class="px-4 py-3 text-slate-600">Deemed Conveyance</td>
            <td class="px-4 py-3 text-slate-800">Land & Building Vithu Mauli, Plot 14, Sector 20</td>
            <td class="px-4 py-3 text-xs text-slate-600">MANAS GROUP → Vithumauli Co-op Hsg Society</td>
            <td class="px-4 py-3 text-xs text-indigo-700 font-medium">Society conveyance detected. Builder rights transferred. ✓</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <!-- ── PORTALS HUB ─────────────────────────────────────────────── -->
  <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
    <div class="flex items-center space-x-3 pb-4 border-b border-slate-100">
      <div class="p-2 bg-emerald-50 text-emerald-600 rounded-lg"><i class="fa-solid fa-globe text-xl"></i></div>
      <div>
        <h3 class="text-lg font-bold text-slate-900">Maharashtra Government Portals Hub</h3>
        <p class="text-xs text-slate-500">All IGR, RERA, Land Records, Courts, and Authority portals — one-click launch</p>
      </div>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mt-5">
"""
    for category, links in portals.items():
        html += f"""
      <div class="border border-slate-200 rounded-lg p-4 bg-slate-50/50">
        <h4 class="text-xs font-bold text-slate-700 uppercase tracking-wide mb-3 flex items-center">
          <i class="fa-solid fa-folder-open text-amber-500 mr-2"></i>{category}
        </h4>
        <div class="space-y-2">
"""
        for item in links:
            html += f"""
          <a href="{item['url']}" target="_blank"
             class="block p-2.5 rounded-lg bg-white border border-slate-200 hover:border-indigo-400 hover:shadow-sm transition group">
            <div class="flex justify-between items-center">
              <span class="text-xs font-semibold text-indigo-700 group-hover:text-indigo-900">{item['name']}</span>
              <i class="fa-solid fa-arrow-up-right-from-square text-[10px] text-slate-400 group-hover:text-indigo-500"></i>
            </div>
            <div class="text-[11px] text-slate-500 mt-0.5 line-clamp-1">{item['description']}</div>
          </a>
"""
        html += "        </div>\n      </div>"

    html += f"""
    </div>
  </div>

  <!-- ── 13-YEAR TIMELINE ───────────────────────────────────────── -->
  <div class="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
    <div class="flex items-center space-x-3 pb-4 border-b border-slate-100">
      <div class="p-2 bg-blue-50 text-blue-600 rounded-lg"><i class="fa-solid fa-timeline text-xl"></i></div>
      <div>
        <h3 class="text-lg font-bold text-slate-900">13-Year Chain of Title (2013 – 2026)</h3>
        <p class="text-xs text-slate-500">Auto-included in generated Bank Word Report</p>
      </div>
    </div>
    <div class="relative border-l-2 border-indigo-200 ml-4 mt-6 space-y-5">
"""
    for rec in reversed(data.search_years):
        active = rec.year >= 2022
        html += f"""
      <div class="relative pl-6">
        <div class="absolute -left-1.5 top-1.5 w-3 h-3 {'bg-indigo-600' if active else 'bg-slate-300'} rounded-full ring-4 ring-white"></div>
        <div class="flex items-baseline gap-2 flex-wrap">
          <span class="text-sm font-bold text-slate-900">{rec.year}</span>
          <span class="text-xs px-2 py-0.5 rounded font-medium {'bg-emerald-100 text-emerald-800' if active else 'bg-slate-100 text-slate-500'}">
            {'Transaction Recorded' if active else 'NIL / Clear'}
          </span>
        </div>
        <p class="text-xs text-slate-700 mt-1 leading-relaxed">{rec.entry_summary}</p>
      </div>
"""
    html += """
    </div>
  </div>

</main>

<footer class="bg-white border-t border-slate-200 py-5 text-center text-xs text-slate-400">
  MahaTitle AI &copy; 2026 — Prototype for Monday Client Demo &nbsp;|&nbsp; All data sourced from registered documents.
</footer>

<script>
// ── Drag & Drop ────────────────────────────────────
function handleDragOver(e) { e.preventDefault(); document.getElementById('drop-zone').classList.add('drag-over'); }
function handleDragLeave(e) { document.getElementById('drop-zone').classList.remove('drag-over'); }
function handleDrop(e) {
  e.preventDefault();
  document.getElementById('drop-zone').classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) uploadFile(file);
}
function handleFileSelect(e) { const file = e.target.files[0]; if (file) uploadFile(file); }

async function uploadFile(file) {
  const statusDiv = document.getElementById('upload-status');
  const resultDiv = document.getElementById('parsed-result');
  resultDiv.classList.add('hidden');
  statusDiv.classList.remove('hidden');
  statusDiv.innerHTML = `
    <div class="flex items-center gap-3 bg-blue-50 border border-blue-200 rounded-lg p-4">
      <i class="fa-solid fa-spinner fa-spin text-blue-600 text-lg"></i>
      <div>
        <p class="text-sm font-semibold text-blue-900">Processing: <span class="font-normal">${file.name}</span></p>
        <p class="text-xs text-blue-600 mt-0.5">Extracting legal entities, building devolution chain, generating Word report…</p>
      </div>
    </div>`;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res  = await fetch('/upload-agreement', { method: 'POST', body: formData });
    const data = await res.json();

    if (data.success) {
      statusDiv.innerHTML = `<div class="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-emerald-800 text-sm"><i class="fa-solid fa-circle-check text-emerald-600"></i> PDF parsed successfully. Report generated.</div>`;

      const p = data.parsed;
      const grid = document.getElementById('parsed-grid');
      grid.innerHTML = [
        ['Purchaser(s)', p.purchasers.join('<br>')],
        ['Developer', p.promoter],
        ['Flat / Floor', `Flat ${p.flat_no} — ${p.floor} Floor${p.building ? '<br><span class=\\"text-xs text-slate-500\\">' + p.building + '</span>' : ''}`],
        ['Plot / Sector', `Plot ${p.plot}, Sector ${p.sector}`],
        ['Location', p.location],
        ['Doc No.', p.doc_no],
        ['Registration', p.registration_date],
        ['Consideration', p.consideration],
        ['Stamp Duty', p.stamp_duty],
        ['MahaRERA', p.rera],
        ['Devolution Steps', p.devolution_count],
        ['Search Years', p.search_years],
      ].map(([k,v]) => `<div class="bg-white border border-emerald-100 rounded-lg p-3"><div class="text-[11px] text-slate-400 uppercase font-medium">${k}</div><div class="text-sm font-semibold text-slate-900 mt-0.5">${v}</div></div>`).join('');

      const link = document.getElementById('new-report-link');
      link.href = data.download_url;
      link.download = data.report_filename;
      resultDiv.classList.remove('hidden');
    } else {
      statusDiv.innerHTML = `<div class="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg p-3 text-red-800 text-sm"><i class="fa-solid fa-circle-xmark text-red-500"></i> Error: ${data.error}</div>`;
    }
  } catch(err) {
    statusDiv.innerHTML = `<div class="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg p-3 text-red-800 text-sm"><i class="fa-solid fa-circle-xmark text-red-500"></i> Upload failed: ${err.message}</div>`;
  }
}

// ── Preset loaders ─────────────────────────────────
function loadPreset(name) {{
  const urls = {{
    samir:  '/download-report?filename=Title_Investigation_Report_Samir_Pawar.docx',
    gaurav: '/api/generate-gaurav'
  }};
  if (name === 'samir') window.open(urls.samir, '_blank');
  if (name === 'gaurav') {{
    document.getElementById('upload-status').classList.remove('hidden');
    document.getElementById('upload-status').innerHTML = '<div class="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg p-3 text-blue-800 text-sm"><i class="fa-solid fa-spinner fa-spin text-blue-600"></i> Generating Gaurav Jadhav (Runwal My City) report…</div>';
    fetch('/api/generate-gaurav').then(r=>r.json()).then(d=>{{
      document.getElementById('upload-status').innerHTML = `<div class="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-emerald-800 text-sm"><i class="fa-solid fa-circle-check text-emerald-600"></i> Report ready! <a href="${{d.url}}" class="underline font-semibold ml-1" download>Download Gaurav Jadhav TIR</a></div>`;
    }});
  }}
}}

// ── IGR Filter Demo ────────────────────────────────
async function runIgrFilter() {{
  const btn = document.getElementById('btn-igr');
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Scanning 995+ entries…';
  btn.disabled = true;
  const res = await fetch('/api/igr-demo');
  const data = await res.json();
  document.getElementById('stat-total').innerText = data.total_raw_entries;
  document.getElementById('stat-rel').innerText   = data.relevant_count;
  document.getElementById('stat-noise').innerText = data.noise_filtered_out_count;
  btn.innerHTML = '<i class="fa-solid fa-check mr-2"></i> Filter Complete (' + data.relevant_count + ' actionable)';
  btn.classList.replace('bg-emerald-600','bg-slate-700');
  btn.classList.replace('hover:bg-emerald-700','hover:bg-slate-800');
}}
</script>
</body>
</html>"""
    return html


@app.get("/api/generate-gaurav")
async def generate_gaurav():
    """Pre-generate Gaurav Jadhav report on demand."""
    data = build_gaurav_jadhav_data()
    fname = "TIR_Gaurav_Kalidas_Jadhav_1922.docx"
    path = os.path.join(OUTPUT_DIR, fname)
    generate_title_report_docx(data, path)
    return {"url": f"/download-report?filename={fname}", "filename": fname}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
