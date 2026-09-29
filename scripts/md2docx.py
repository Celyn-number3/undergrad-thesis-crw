"""Markdown 转 Word（论文排版：宋体/黑体、1.5 倍行距、首行缩进、三线表风格边框、插图）。

用法：python scripts/md2docx.py 输入.md 输出.docx
图片写法：![图注](相对仓库根目录的路径)，图注会作为图题居中显示在图下方。
"""
import re,sys
from docx import Document
from docx.shared import Pt,Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
src,dst=sys.argv[1],sys.argv[2]
d=Document()
for s in d.sections: s.top_margin=s.bottom_margin=Cm(2.5); s.left_margin=s.right_margin=Cm(2.8)
def font(r,name='宋体',size=12,bold=None):
    r.font.name='Times New Roman'; r.font.size=Pt(size)
    r._element.rPr.rFonts.set(qn('w:eastAsia'),name)
    if bold is not None: r.bold=bold
def runs(p,text,size=12,name='宋体'):
    for i,part in enumerate(re.split(r'\*\*',text)):
        if part: font(p.add_run(part),name,size,bold=(i%2==1))
def para(text,indent=True,size=12):
    p=d.add_paragraph(); pf=p.paragraph_format
    pf.line_spacing=1.5; pf.space_after=Pt(0)
    if indent: pf.first_line_indent=Pt(size*2)
    runs(p,text,size); return p
def border(t):
    tbl=t._tbl; pr=tbl.tblPr; b=OxmlElement('w:tblBorders')
    for e in('top','left','bottom','right','insideH','insideV'):
        x=OxmlElement('w:'+e); x.set(qn('w:val'),'single'); x.set(qn('w:sz'),'4'); b.append(x)
    pr.append(b)
lines=open(src,encoding='utf-8').read().split('\n'); i=0
while i<len(lines):
    l=lines[i]
    if l.startswith('# '):
        p=d.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(18)
        font(p.add_run(l[2:]),'黑体',18,True)
    elif l.startswith('## '):
        p=d.add_paragraph(); p.paragraph_format.space_before=Pt(12); p.paragraph_format.space_after=Pt(6)
        font(p.add_run(l[3:]),'黑体',14,True)
    elif l.startswith('### '):
        p=d.add_paragraph(); p.paragraph_format.space_before=Pt(6); p.paragraph_format.space_after=Pt(3)
        font(p.add_run(l[4:]),'黑体',12,True)
    elif l.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            c=[x.strip() for x in lines[i].strip('|').split('|')]
            if not all(re.fullmatch(r'-+',x) for x in c): rows.append(c)
            i+=1
        t=d.add_table(rows=len(rows),cols=len(rows[0])); border(t); t.alignment=WD_ALIGN_PARAGRAPH.CENTER
        for r,row in enumerate(rows):
            for c,v in enumerate(row):
                cell=t.cell(r,c); cell.text=''; p=cell.paragraphs[0]
                runs(p,v.replace('**',''),10.5,'黑体' if r==0 else '宋体')
                if r==0: p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        d.add_paragraph(); continue
    elif l.startswith('```'):
        i+=1
        while not lines[i].startswith('```'):
            p=d.add_paragraph(); p.paragraph_format.space_after=Pt(0); p.paragraph_format.left_indent=Cm(1)
            font(p.add_run(lines[i]),'宋体',10.5); i+=1
    elif l.startswith('!['):
        m=re.match(r'!\[(.*?)\]\((.*?)\)',l)
        d.add_picture(m.group(2),width=Cm(14.5)); d.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
        p=para(m.group(1),indent=False,size=10.5); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    elif l.startswith('> '):
        p=para(l[2:],indent=False,size=10.5); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    elif l.strip()=='---': pass
    elif re.match(r'^- ',l): para('• '+l[2:],indent=True)
    elif re.match(r'^\d+\. ',l): para(l,indent=True)
    elif l.startswith('['):
        p=para(l,indent=False,size=10.5); p.paragraph_format.left_indent=Pt(21); p.paragraph_format.first_line_indent=Pt(-21)
    elif l.strip(): para(l)
    i+=1
d.save(dst)
