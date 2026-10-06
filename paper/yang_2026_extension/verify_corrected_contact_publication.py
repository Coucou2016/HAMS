"""Check final scientific tables, retained equations/images, and rendered pages."""
from pathlib import Path
import hashlib
import json

from docx import Document
import fitz
from PIL import Image, ImageDraw
from refine_review_20260927 import structural_record

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / 'revision_corrected_20260928'
CASE = ROOT / 'RocketRecoveryCases/Chrono_LeggedRecovery_Corrected20260927_v2'


def main():
    source = HERE / 'revision_20260927/HAMS_manuscript_refined_20260927.docx'
    docx = OUT / 'HAMS_manuscript_corrected_20260928.docx'
    pdf = OUT / 'HAMS_manuscript_corrected_20260928.pdf'
    before, after = structural_record(source), structural_record(docx)
    assert before['math'] == after['math']
    assert len(after['tables']) == 4 and after['inline_shapes'] == 8
    assert before['tables'][0] == after['tables'][0]
    assert before['tables'][2] == after['tables'][2]
    changed_images = [k for k,v in after['media'].items() if before['media'].get(k) != v]
    assert len(changed_images) == 1, changed_images
    document = Document(docx)
    report = json.loads((CASE / 'chrono-same-platform-multibody-report.json').read_text(encoding='utf-8'))
    values = report['time_step_convergence']['values']
    for row, key, dt in zip(document.tables[3].rows[1:], ['dt','dt_over_2','dt_over_4'], [.5,.25,.125]):
        v = values[key]
        expected = [f'{dt:g} ms', f'{v["max_leg_contact_force_kn"]/1000:.3f} MN',
                    f'{v["max_leg_stroke_m"]*1000:.2f} mm', f'{v["max_contact_penetration_m"]*1000:.2f} mm',
                    f'{v["touchdown_span_s"]:.4f} s']
        assert [c.text for c in row.cells] == expected
    pages = fitz.open(pdf)
    qa = OUT / 'visual_qa'
    qa.mkdir(exist_ok=True)
    page_checks = []
    thumbnails = []
    for i,page in enumerate(pages):
        spans = [s for b in page.get_text('dict')['blocks'] if 'lines' in b for line in b['lines'] for s in line['spans']]
        outside = [s['text'] for s in spans if not (fitz.Rect(page.rect.x0-1,page.rect.y0-1,page.rect.x1+1,page.rect.y1+1).contains(fitz.Rect(s['bbox'])))]
        page_checks.append({'page': i+1, 'nonblank': bool(page.get_text().strip()), 'outside_page': outside})
        pix = page.get_pixmap(matrix=fitz.Matrix(.65,.65))
        bitmap = Image.frombytes('RGB', [pix.width,pix.height], pix.samples)
        thumbnails.append(bitmap)
    for start in range(0,len(thumbnails),6):
        group = thumbnails[start:start+6]
        w,h = max(x.width for x in group), max(x.height for x in group)
        sheet = Image.new('RGB',(3*w,2*(h+26)),'#e8e8e8')
        draw = ImageDraw.Draw(sheet)
        for j,im in enumerate(group):
            x,y = (j%3)*w,(j//3)*(h+26)
            sheet.paste(im,(x,y+26))
            draw.text((x+8,y+5),str(start+j+1),fill='black')
        sheet.save(qa / f'overview-{start//6+1}.png')
    result = {'pdf_pages':len(pages),'native_math_objects':len(after['math']),
              'only_figure6_replaced':True, 'tables1_and3_preserved':True,
              'table4_matches_corrected_report':True, 'page_checks':page_checks,
              'automated_checks_pass':all(x['nonblank'] and not x['outside_page'] for x in page_checks),
              'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
              'scope':'Publication consistency and page bounds; scientific numerical failures remain reported'}
    (OUT / 'delivery-validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'page_checks'},indent=2))


if __name__ == '__main__':
    main()
