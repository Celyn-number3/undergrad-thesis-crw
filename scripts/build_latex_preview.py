from pathlib import Path
import re, json, subprocess, hashlib, shutil, os
root=Path.cwd()
source=root/'docs/mcp-thesis-draft.md'
out=root/'docs/latex-preview'
assert (out/'logs/conversion-check.json').exists(), 'Only revise the preview created by this task'
md=source.read_text(encoding='utf-8')
# Explicit rebuild from the revised Markdown source.
protected=[source,root/'docs/thesis-draft.docx']+[root/p for p in ['docs/mcp-thesis-abstract.md','docs/mcp-thesis-ch1.md','docs/mcp-thesis-ch2.md','docs/mcp-thesis-ch3-ch4.md','docs/mcp-thesis-ch5.md','scripts/build_draft.py','scripts/md2docx.py','scripts/check_numbers.py','docs/mcp-literature-review.md']]
hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
out.mkdir(exist_ok=True);(out/'sections').mkdir(exist_ok=True);(out/'figures').mkdir(exist_ok=True);(out/'logs').mkdir(exist_ok=True)
pandoc=root/'runtime/pandoc/pandoc.exe'
# Explicit, reviewed re-typesetting of the source equations, with unchanged numbering.
formula={
1:r'\operatorname{tfidf}(t,d)=[1+\log\operatorname{tf}(t,d)]\left\{1+\log\frac{1+N}{1+\operatorname{df}(t)}\right\}',
2:r'P(y=k\mid x)=\frac{\exp(w_k\cdot x+b_k)}{\sum_j\exp(w_j\cdot x+b_j)}',
3:r'\min\;\frac12\lVert w\rVert^2+C\sum_i\max\!\left(0,1-y_i(w\cdot x_i+b)\right)',
4:r'\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\!\left(\frac{QK^{\mathsf T}}{\sqrt{d_k}}\right)V',
5:r'p_k=\frac{\exp(z_k)}{\sum_j\exp(z_j)},\quad k\in\{\text{消极},\text{中性},\text{积极}\}',
6:r'h=W_0x+\Delta Wx=W_0x+\frac{\alpha}{r}BAx',
7:r'\begin{aligned}P_k&=\frac{\mathrm{TP}_k}{\mathrm{TP}_k+\mathrm{FP}_k},\quad R_k=\frac{\mathrm{TP}_k}{\mathrm{TP}_k+\mathrm{FN}_k},\\ \mathrm{F1}_k&=\frac{2P_kR_k}{P_k+R_k}\end{aligned}',
8:r'\text{Macro-F1}=\frac1K\sum_k\mathrm{F1}_k',
9:r'F=\frac{\sum_i n_i(\bar y_i-\bar y)^2/(g-1)}{\sum_i\sum_j(y_{ij}-\bar y_i)^2/(N-g)}',
10:r'\chi^2=\frac{(\lvert b-c\rvert-1)^2}{b+c}',
11:r'\tilde p_{(i)}=\max_{j\le i}\min\{1,(m-j+1)p_{(j)}\}',
12:r'\mathrm{ECE}=\sum_m\frac{\lvert B_m\rvert}{n}\,\bigl\lvert\operatorname{acc}(B_m)-\operatorname{conf}(B_m)\bigr\rvert',
13:r'p_k=\frac{\exp(z_k/T)}{\sum_j\exp(z_j/T)}',
14:r'\hat q=s\text{ 的第 }\lceil(n+1)(1-\alpha)\rceil\text{ 个次序统计量}',
15:r'P\bigl(y\in C(x)\bigr)\ge 1-\alpha',
16:r'\kappa=\frac{p_o-p_e}{1-p_e}',
17:r'q=\frac{1+\sqrt{6p_o-2}}{3}'
}
code_formula={
'P(y = c | x)':r'P(y=c\mid x)=\frac{\exp(z_c)}{\sum_j\exp(z_j)},\quad c,j\in\{\text{消极},\text{中性},\text{积极}\}',
'h = W x':r'h=Wx+\frac{\alpha}{r}BAx',
'Macro-F1 =':r'\text{Macro-F1}=\frac{\mathrm{F1}_{\text{消极}}+\mathrm{F1}_{\text{中性}}+\mathrm{F1}_{\text{积极}}}{3}',
'χ² =':r'\chi^2=\frac{(\lvert n_{01}-n_{10}\rvert-1)^2}{n_{01}+n_{10}}',
'ECE =':formula[12]
}
symbols={'→':r'\to','α':r'\alpha','κ':r'\kappa','π':r'\pi','τ':r'\tau','χ':r'\chi','Δ':r'\Delta','Σ':r'\Sigma','ℝ':r'\mathbb{R}','∈':r'\in','−':'-','×':r'\times','±':r'\pm','≈':r'\approx','≤':r'\le','≥':r'\ge','⌈':r'\lceil','⌉':r'\rceil','√':r'\surd','‖':r'\Vert','·':r'\cdot'}
sub=str.maketrans('₀₁₂₃₍₎ₖₘᵢⱼ','0123()kmij');sup=str.maketrans('⁰¹²³⁴⁵⁸⁹⁻ᵀ','01234589-T')
def inline_math(s):
 s=s.replace('q̂',r'$\hat q$').replace('ȳ',r'$\bar y$').replace('p̃',r'$\tilde p$')
 s=re.sub('[₀₁₂₃₍₎ₖₘᵢⱼ]+',lambda m:'$_{'+m[0].translate(sub)+'}$',s)
 s=re.sub('[⁰¹²³⁴⁵⁸⁹⁻ᵀ]+',lambda m:'$^{'+m[0].translate(sup)+'}$',s)
 return ''.join('$'+symbols[c]+'$' if c in symbols else c for c in s).replace('$$','')
def citations(s):
 def repl(m):
  ids=[]
  for part in m[1].split(','):
   if '-' in part:
    a,b=map(int,part.split('-'));ids.extend(range(a,b+1))
   else:ids.append(int(part))
  assert all(1<=n<=33 for n in ids)
  return r'\cite{'+','.join('ref'+str(n) for n in ids)+'}'
 return re.sub(r'\[(\d+(?:[-,]\d+)*)\]',repl,s)
def text_pre(s):
 s=inline_math(s);s=re.sub(r'\$([^$]+)\$',lambda m:'`'+r'\('+m[1]+r'\)'+'`{=latex}',s);s=citations(s)
 s=re.sub(r'([图表])\s*([1-5]-\d+)',lambda m:'`'+m[1]+'~\\ref{'+('fig:' if m[1]=='图' else 'tab:')+m[2]+'}'+'`{=latex}',s)
 return s
# Table cells are escaped directly; math and citation commands are protected first.
def cell(s, cite=True):
 s=inline_math(s)
 if cite:s=citations(s)
 tokens=[]
 def hold(m):tokens.append(m[0]);return 'ZZTOKEN'+str(len(tokens)-1)+'ZZ'
 s=re.sub(r'\$[^$]+\$|\\cite\{[^}]+\}',hold,s)
 escapes={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_\allowbreak{}','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}
 s=''.join(escapes.get(c,c) for c in s)
 s=re.sub(r'\*\*(.*?)\*\*',lambda m:r'\textbf{'+m[1]+'}',s)
 s=s.replace('-',r'-\allowbreak{}').replace('/',r'/\allowbreak{}')
 for i,t in enumerate(tokens):s=s.replace('ZZTOKEN'+str(i)+'ZZ',t)
 return s

def raw(s):return '\n```{=latex}\n'+s+'\n```\n'
weights={'2-1':[.20,.23,.25,.32],'3-1':[.78,.22],'3-5':[.19,.40,.13,.28],'3-6':[.19,.65,.16],
'4-1':[.30,.07,.20,.20,.23],'4-2':[.40,.20,.20,.20],'4-3':[.20,.20,.12,.12,.12,.12,.12],
'4-4':[.20,.20,.12,.24,.24],'4-6':[.20,.20,.12,.14,.34],'4-7':[.30,.14,.14,.14,.14,.14],
'4-8':[.40,.20,.20,.20],'4-9':[.28,.10,.10,.13,.13,.13,.13],
'4-11':[.30,.10,.15,.15,.15,.15],'4-12':[.46,.54],'4-13':[.32,.12,.16,.20,.20],
'4-14':[.32,.14,.18,.18,.18],'4-15':[.40,.30,.30],'4-16':[.29,.13,.13,.15,.15,.15],'4-17':[.08,.18,.61,.13]}
stats={'headings':0,'tables':[],'figures':[],'numbered_equations':[],'unnumbered_equations':[]}
def table(rows,cap,note=None):
 m=re.match(r'表\s+(\d+-\d+)\s+(.*)',cap);num,title=m.groups();n=len(rows[0]);w=weights.get(num,[1/n]*n);w=[x/sum(w) for x in w]
 col=''.join(r'>{\raggedright\arraybackslash}p{\dimexpr '+f'{x:.6f}'+r'\linewidth-'+f'{2*n*x:.6f}'+r'\tabcolsep\relax}' for x in w)
 head=' & '.join(r'\textbf{'+cell(c)+'}' for c in rows[0])+r' \\'
 lines=[r'\begin{table}[htbp]',r'\centering',r'\begin{minipage}{\textwidth}',r'\setlength{\tabcolsep}{3pt}',r'\renewcommand{\arraystretch}{1.16}',r'\setstretch{1.0}\fontsize{10.5}{13.5}\selectfont',r'\caption{'+cell(title)+r'}\label{tab:'+num+r'}',r'\begin{tabular}{'+col+'}',r'\toprule',head,r'\midrule']
 for row in rows[1:]:
  assert len(row)==n
  lines.append(' & '.join(cell(c) for c in row)+r' \\')
 lines.append(r'\bottomrule\end{tabular}')
 if note:lines.append(r'\par\vspace{3pt}{\fontsize{10}{12.5}\selectfont '+cell(note)+r'\par}')
 lines += [r'\end{minipage}',r'\end{table}']
 stats['tables'].append({'number':num,'rows':len(rows),'columns':n,'source_cells':rows,'note':note})
 return raw('\n'.join(lines))

parts={};current=None;lines=md.splitlines();i=0;cap=None
while i<len(lines):
 l=lines[i]
 if l.startswith('# '):
  title=l[2:];current='abstract-zh' if title=='摘要' else 'abstract-en' if title=='Abstract' else 'references' if title=='参考文献' else 'ch'+re.match(r'第(\d+)章',title)[1]
  parts[current]=[];stats['headings']+=1
  if current.startswith('ch'):parts[current].append(raw(r'\clearpage\section{'+re.sub(r'^第\d+章\s*','',title)+'}'))
 elif l.startswith('##'):
  level=len(l)-len(l.lstrip('#'));title=re.sub(r'^#+\s*\d+(?:\.\d+)*\s+','',l);stats['headings']+=1
  parts[current].append(raw((r'\FloatBarrier' if level==2 else '')+('\\subsection' if level==2 else '\\subsubsection')+'{'+cell(title)+'}'))
 elif l.startswith('> 表 '):cap=l[2:]
 elif l.startswith('|'):
  rows=[]
  while i<len(lines) and lines[i].startswith('|'):
   row=[x.strip() for x in lines[i].strip('|').split('|')]
   if not all(re.fullmatch(r':?-+:?',x) for x in row):rows.append(row)
   i+=1
  j=i
  while j<len(lines) and not lines[j].strip():j+=1
  note=lines[j] if j<len(lines) and lines[j].startswith('注：') else None
  if note:i=j+1
  assert cap;parts[current].append(table(rows,cap,note));cap=None;continue
 elif l.startswith('!['):
  m=re.match(r'!\[(图\s+(\d+-\d+)\s+(.*?))\]\((.*?)\)',l);_,num,title,path=m.groups()
  p=root/path
  if p.with_suffix('.pdf').exists() and 'editorial-20261013' in path:p=p.with_suffix('.pdf')
  dest=out/'figures'/p.name;shutil.copyfile(p,dest)
  stats['figures'].append({'number':num,'source':path,'file':'figures/'+p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  parts[current].append(raw(r'\begin{figure}[htbp]\centering'+'\n'+r'\includegraphics[width=\linewidth,height=0.80\textheight,keepaspectratio]{figures/'+p.name+'}\n'+r'\caption{'+cell(title)+r'}\label{fig:'+num+r'}\end{figure}'))
 elif l.startswith('```'):
  block=[];i+=1
  while not lines[i].startswith('```'):block.append(lines[i]);i+=1
  content='\n'.join(block);key=next((k for k in code_formula if content.startswith(k)),None)
  if key:
   parts[current].append(raw(r'\['+code_formula[key]+r'\]'));stats['unnumbered_equations'].append(content)
  else:parts[current].append(raw(r'\begin{quote}\small '+r'\par '.join(cell(x,False) for x in block)+r'\end{quote}'))
 elif re.search(r'（2-\d+）$',l):
  k=int(re.search(r'（2-(\d+)）$',l)[1]);parts[current].append(raw(r'\begin{equation}'+formula[k]+r'\tag{2-'+str(k)+r'}\label{eq:2-'+str(k)+r'}\end{equation}'));stats['numbered_equations'].append({'number':'2-'+str(k),'source':l.strip(),'latex':formula[k]})
 elif current=='references' and re.match(r'^\[\d+\]',l):
  m=re.match(r'^\[(\d+)\]\s*(.*)',l);parts[current].append(raw(r'\bibitem['+m[1]+r']{ref'+m[1]+'} '+cell(m[2],False)))
 else:parts[current].append(text_pre(l))
 i+=1
assert len(stats['tables'])==24 and len(stats['figures'])==9 and len(stats['numbered_equations'])==17
for key,body in parts.items():
 c=subprocess.run([str(pandoc),'-f','markdown+raw_tex+raw_attribute-smart','-t','latex','--wrap=none'],input='\n'.join(body).encode(),capture_output=True,timeout=30)
 assert c.returncode==0,c.stderr
 (out/'sections'/f'{key}.tex').write_bytes(c.stdout)
# Keep the explicitly edited main.tex rather than overwriting manual layout refinements.
template=out/'main.tex'
assert template.exists()
manifest={'source':str(source.relative_to(root)),'hashes_before':hashes,'template':str(template.relative_to(root)),'template_sha256':hashlib.sha256(template.read_bytes()).hexdigest(),'counts':{k:len(v) if isinstance(v,list) else v for k,v in stats.items()},'conversion_details':stats,'scope':'Editorial revision; source-synchronized 24 tables, 9 figures, 17 native equations; archived experimental results unchanged'}
(out/'logs/conversion-check.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
assert all(hashlib.sha256(Path(root/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
print(json.dumps({'output':str(out),'counts':manifest['counts'],'protected_unchanged':True},ensure_ascii=False))
