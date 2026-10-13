"""Reproduce descriptive error analysis from saved predictions; no model loading.
Run from project root: runtime/python/python.exe -I -B scripts/analyze_error_cases.py
Writes only outputs/analysis/editorial-20261013/. Labels are observed dataset labels.
"""
from pathlib import Path
import csv, hashlib, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/analysis/editorial-20261013'
MODELS = {'TF-IDF+LR': 'tfidf_lr', 'RoBERTa': 'chinese-roberta-wwm-ext_s42',
          'Qwen3-8B LoRA': 'Qwen3-8B_lora_r16_s42'}
LABELS = ['消极', '中性', '积极']

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frames = {}; hashes = {}
    for name, stem in MODELS.items():
        p = ROOT / 'outputs/predictions' / (stem + '.csv')
        hashes[str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
        with p.open(encoding='utf-8-sig', newline='') as f: frames[name] = list(csv.DictReader(f))
    base = frames['TF-IDF+LR']; n = len(base)
    assert n == 1713
    for rows in frames.values():
        assert [(r['text'], r['label']) for r in rows] == [(r['text'], r['label']) for r in base]
    data_path = ROOT / 'data/processed/finfe/test.jsonl'
    test = [json.loads(s) for s in data_path.read_text(encoding='utf-8').splitlines() if s]
    assert [(r['text'], int(r['label'])) for r in base] == [(r['text'], int(r['label'])) for r in test]
    hashes[str(data_path.relative_to(ROOT))] = hashlib.sha256(data_path.read_bytes()).hexdigest()
    result = {'n': n, 'label_map': dict(enumerate(LABELS)), 'inputs_sha256': hashes, 'models': {}}
    for name, rows in frames.items():
        cm = np.zeros((3, 3), dtype=int)
        for row in rows: cm[int(row['label']), int(row['pred'])] += 1
        metrics = []
        for c in range(3):
            tp = int(cm[c,c]); support = int(cm[c].sum()); pp = int(cm[:,c].sum())
            precision = tp/pp if pp else 0; recall = tp/support
            f1 = 2*precision*recall/(precision+recall) if precision+recall else 0
            metrics.append({'class':LABELS[c], 'support':support, 'precision':precision, 'recall':recall, 'f1':f1})
        errors = n-int(np.trace(cm)); involving_neutral = int(cm[1].sum()+cm[:,1].sum()-2*cm[1,1])
        result['models'][name] = {'confusion': cm.tolist(), 'accuracy':float(np.trace(cm)/n), 'macro_f1':sum(m['f1'] for m in metrics)/3, 'errors':errors, 'neutral_involved_errors':involving_neutral, 'neutral_error_share':involving_neutral/errors, 'class_metrics':metrics}
    a=frames['RoBERTa']; b=frames['Qwen3-8B LoRA']
    result['paired_errors']={'roberta_wrong_qwen_right':sum(x['pred']!=x['label'] and y['pred']==y['label'] for x,y in zip(a,b)), 'roberta_right_qwen_wrong':sum(x['pred']==x['label'] and y['pred']!=y['label'] for x,y in zip(a,b)), 'both_wrong':sum(x['pred']!=x['label'] and y['pred']!=y['label'] for x,y in zip(a,b))}
    # Fixed sampling: six off-diagonal directions, hash-rank ascending, two cases each.
    # This stratified qualitative sample cannot estimate population error-type prevalence.
    cases=[]
    for true in range(3):
        for pred in range(3):
            if true==pred: continue
            ids=[i for i,r in enumerate(b) if int(r['label'])==true and int(r['pred'])==pred]
            ids.sort(key=lambda i:hashlib.sha256(('error-audit-v1\0'+b[i]['text']).encode()).hexdigest())
            for rank,i in enumerate(ids[:2],1):
                r=b[i];cases.append({'direction':f'{true}->{pred}', 'rank_in_stratum':rank, 'data_row_1based':i+1,'csv_line':i+2,'text':r['text'],'observed_label':LABELS[true],'qwen_pred':LABELS[pred], 'qwen_max_probability':max(float(r['p'+str(k)]) for k in range(3)), 'roberta_pred':LABELS[int(a[i]['pred'])],'tfidf_pred':LABELS[int(base[i]['pred'])]})
    with (OUT/'error_cases.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(cases[0]));w.writeheader();w.writerows(cases)
    result['case_selection']='SHA256(error-audit-v1 + NUL + original text), two cases per ordered misclassification pair; first per pair displayed in thesis'
    result['cases']=cases
    (OUT/'error_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    plt.rcParams.update({'font.family':'Microsoft YaHei','axes.unicode_minus':False,'font.size':11.5,'pdf.fonttype':42})
    fig,axs=plt.subplots(1,3,figsize=(7.2,3.1),layout='constrained')
    for ax,(name,m) in zip(axs,result['models'].items()):
        cm=np.array(m['confusion']);percent=cm/cm.sum(axis=1,keepdims=True)
        ax.imshow(percent,cmap='Blues',vmin=0,vmax=1)
        for i in range(3):
            for j in range(3):ax.text(j,i,f'{cm[i,j]}\n{100*percent[i,j]:.1f}%',ha='center',va='center',fontsize=11.5,color='white' if percent[i,j]>.55 else '#172b42')
        ax.set(xticks=range(3),xticklabels=LABELS,yticks=range(3),yticklabels=LABELS,xlabel='预测标签',title=name)
    axs[0].set_ylabel('观测标签')
    for suffix in ['png','pdf']:fig.savefig(OUT/('fig_confusion.'+suffix),dpi=240,bbox_inches='tight')
    plt.close(fig)
    # The two reliability branches explicitly reuse the test set; they are not external validation.
    fig,ax=plt.subplots(figsize=(8,6.6));ax.set(xlim=(0,10),ylim=(0,10));ax.axis('off')
    def box(x,y,w,h,text,color='#e8eff5'):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.07',facecolor=color,edgecolor='#52697d',linewidth=1))
        ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=10)
    def arrow(x,y,a,b):ax.annotate('',xy=(a,b),xytext=(x,y),arrowprops={'arrowstyle':'->','color':'#52697d','lw':1.1})
    box(1.5,8.8,7,1,'FinFE 公开带标签数据\n规范化、去重、冲突处理及跨集合完全重复排除')
    box(.2,7,3,1,'训练集 8802\n模型拟合');box(3.5,7,3,1,'验证集 979\n超参数选择 / 检查点选择');box(6.8,7,3,1,'测试集 1713\n固定预测与观测标签')
    for x in [1.7,5,8.3]:arrow(5,8.8,x,8)
    box(.6,4.7,8.8,1.4,'统一模型比较：TF-IDF、BERT / RoBERTa、LLM 提示与 LoRA\n训练重复：种子 42 / 43 / 44；单次提示与消融另行标注\n测试预测存档；原始概率精度限制单独披露')
    for x in [1.7,5,8.3]:arrow(x,7,x,6.1)
    box(.2,2.3,3,1.5,'RQ1：比较是否可信\n三种子 ANOVA / Tukey\n种子42 配对检验与区间\n多重比较控制')
    box(3.5,2.3,3,1.5,'RQ2：置信度是否可靠\n测试分布内五折温度交叉拟合\n风险—覆盖率；保形校准/评估\n不视为独立部署验证')
    box(6.8,2.3,3,1.5,'RQ3：失效与使用边界\n类条件混淆、固定抽样案例\n共同未曝光样本比较\n噪声与存储精度敏感性')
    for x in [1.7,5,8.3]:arrow(x,4.7,x,3.8)
    box(1,0.4,8,1,'结论限定于当前清洗规则、数据划分与训练配置\n不把点估计优势、未显著差异或边际覆盖率外推为更强保证','#f3eee3')
    for x in [1.7,5,8.3]:arrow(x,2.3,5,1.4)
    for suffix in ['png','pdf']:fig.savefig(OUT/('fig_research_flow.'+suffix),dpi=240,bbox_inches='tight')
    plt.close(fig)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    print(json.dumps({k:{x:y for x,y in v.items() if x!='class_metrics'} for k,v in result['models'].items()},ensure_ascii=False))

if __name__=='__main__': main()
