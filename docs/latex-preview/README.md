# 论文修订稿：LaTeX 源码与编译

修订日期：2026-10-13。使用通用 A4 版式，不是学校正式模板，未填写学校、作者与导师个人信息。

## 文件

- `main.tex`：主文件与已人工调整的版式。
- `sections/`：由 Markdown 转换的摘要、五章正文与参考文献。
- `figures/`：本文实际使用的图；新增流程、混淆矩阵和重绘图优先使用矢量 PDF。
- `main.pdf`：44 页编译成品；24 表、9 图、17 个编号公式、33 篇文献。
- `logs/conversion-check.json`：源稿哈希、逐表数据与转换记录。

修订内容及证据限制详见项目 `docs/mcp-thesis-editorial-revision.md`。

## 原项目中重新编译

在 `docs/latex-preview` 下调用已有 XeLaTeX，连续运行三遍：

```bat
..\..\runtime\texlive\miktex\bin\x64\xelatex.exe --disable-installer --no-shell-escape -interaction=nonstopmode -file-line-error main.tex
```

目录名虽然含 texlive，现有引擎实际为 MiKTeX；部分宏包来自本机 MiKTeX 安装位置，并非完全隔离的便携 TeX Live。此轮未安装新的宏包。

在其他机器上，可使用已安装所需宏包的 XeLaTeX。字体为 Windows 宋体/黑体与 Times New Roman；非 Windows 环境需自行配置 CJK 字体与 `fontset`。源码包不包含 runtime、字体或模型权重。

## 内容更新顺序

在原项目根目录运行：

```bat
runtime\python\python.exe -I -B scripts\build_draft.py
runtime\python\python.exe -I -B scripts\md2docx.py docs\mcp-thesis-draft.md docs\thesis-draft.docx
runtime\python\python.exe -I -B scripts\build_latex_preview.py
```

随后按上面的命令编译三遍。LaTeX 构建脚本保留人工维护的 `main.tex`，只更新章节、所引用图与转换记录。Word 与 PDF 内容同步，但不是同一个分页引擎。

新增错误分析可通过 `scripts/analyze_error_cases.py` 重现；重绘图可通过 `scripts/render_thesis_figures.py` 重现。这两项只读取已有预测/结果，不加载模型，不训练，不推理。它们依赖原项目中的数据与预测文件；交付源码包不另外复制全部实验数据。

## 核验边界

最终编译无溢出、缺字、未定义引用或编译错误；已核对表格内容与关键 PDF 页面。机器核验不等于研究结论被外部独立验证。Word 已检查结构与原生公式，未在 Microsoft Word 内逐页渲染。本稿仍保留单一数据集、有限训练重复、测试分布内校准、历史概率精度及缺少独立复标等限制。
