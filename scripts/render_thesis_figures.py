"""Redraw thesis assets from archived predictions/metrics; does not load models.
Run from project root. Existing analysis files are read-only.
"""
from pathlib import Path
import runpy,json,hashlib,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path.cwd();OUT=ROOT/'outputs/analysis/editorial-20261013'
s=runpy.run_path('src/analysis/stats.py',run_name='thesis_plot_source')
OUT.mkdir(exist_ok=True)
cal,curves,scaled=s['calibration']() # Same archived probabilities and original cross-fitting rule.
old=list(csv.DictReader(Path('outputs/analysis/calibration.csv').open(encoding='utf-8-sig')))
new=cal.to_dict('records')
assert isinstance(old,list)
for x,y in zip(old,new):
 assert x['模型']==y['模型']
 for k in ['ECE','NLL','温度T(均值)','缩放后ECE','缩放后NLL']:assert abs(float(x[k])-y[k])<1e-10,(k,x[k],y[k])
plt.rcParams.update({'font.family':'Microsoft YaHei','font.size':11,'pdf.fonttype':42})
fig,axes=plt.subplots(3,2,figsize=(6.4,7.1),layout='constrained')
for ax,n in zip(axes.flat,curves):
 for c,style,color,lab in [(curves[n],'o-','#28658c','原始'),(scaled[n],'s--','#c77a32','交叉拟合后')]:
  xx,yy,nn=zip(*c);ax.plot(xx,yy,style,color=color,ms=3.5,lw=1.3,label=lab)
 ax.plot([0,1],[0,1],':',color='#999999',lw=1)
 ax.set(xlim=(0,1),ylim=(0,1),xticks=[0,.5,1],yticks=[0,.5,1],title=n,xlabel='平均置信度',ylabel='实际准确率')
 ax.set_title(n,fontsize=11);ax.grid(alpha=.15);ax.legend(fontsize=9,loc='upper left')
for ext in ['png','pdf']:fig.savefig(OUT/('fig_reliability.'+ext),dpi=260,bbox_inches='tight')
plt.close(fig)
# Redraw ablations without re-running any model or statistical resampling.
def get(stem):return json.loads((ROOT/'outputs/metrics'/(stem+'.json')).read_text(encoding='utf-8'))['macro_f1']
size=[0,500,1000,2000,4000,8802]
y=[get('Qwen3-8B_zeroshot')]+[get(f'Qwen3-8B_lora_r16_n{n}_s42') for n in size[1:-1]]+[get('Qwen3-8B_lora_r16_s42')]
fig=plt.figure(figsize=(6.4,5.8),layout='constrained');gs=fig.add_gridspec(2,2);a=fig.add_subplot(gs[0,:]);b=fig.add_subplot(gs[1,0]);c=fig.add_subplot(gs[1,1])
a.plot(size,y,'o-',color='#28658c');a.axhline(np.mean([get(f'chinese-roberta-wwm-ext_s{k}') for k in [42,43,44]]),color='#888888',ls='--',label='RoBERTa 全量（三种子均值）')
a.set(xlabel='训练样本数（0 为零样本）',ylabel='Macro-F1',title='(a) 样本量：子样本 3 轮，全量 2 轮');a.legend(fontsize=9);a.grid(alpha=.2)
for ax,labels,vals,title in [(b,['4','8','16','32'],[get(f'Qwen3-8B_lora_r{r}_s42') for r in [4,8,16,32]],'(b) LoRA 秩'),(c,['16位','4位'],[get('Qwen3-8B_lora_r16_s42'),get('Qwen3-8B_lora_r16_4bit_s42')],'(c) 量化精度')]:
 bars=ax.bar(labels,vals,color='#467892',width=.55);ax.set(ylim=(.75,.835),ylabel='Macro-F1',title=title);ax.grid(axis='y',alpha=.2)
 for rect,v in zip(bars,vals):ax.text(rect.get_x()+rect.get_width()/2,v+.002,f'{v:.3f}',ha='center',fontsize=10)
for ext in ['png','pdf']:fig.savefig(OUT/('fig_ablation.'+ext),dpi=260,bbox_inches='tight')
plt.close(fig)
(OUT/'figure_validation.json').write_text(json.dumps({'calibration_matches_archive':True,'calibration_max_tolerance':1e-10,'scope':'redraw; no new training or model inference'},indent=2),encoding='utf-8')
print('Replotted reliability and ablation; original calibration matches.')
