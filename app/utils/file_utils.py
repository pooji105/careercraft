import io
from xhtml2pdf import pisa

def html_to_pdf(html_content):
    pdf = io.BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf)
    if pisa_status.err:
        return None
    pdf.seek(0)
    return pdf

def export_job_match_history_txt(histories):
    """
    Export job match history as a TXT file. Each entry includes timestamp, input, and AI response.
    Returns a BytesIO object.
    """
    output = io.StringIO()
    for hist in histories:
        output.write(f"=== Match History Entry ===\n")
        output.write(f"Timestamp: {hist.created_at.strftime('%Y-%m-%d %H:%M')}\n")
        output.write(f"Input:\n{hist.input_text}\n\n")
        output.write(f"AI Response:\n{hist.matched_roles_json}\n")
        output.write(f"\n--------------------------\n\n")
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    return mem 