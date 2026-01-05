import pdfplumber

pdf = pdfplumber.open('「指導と評価の一体化」のための学習評価に関する参考資料.pdf')
page = pdf.pages[11]  # Page 12 (0-indexed)
chars = page.chars[:30]
for c in chars:
    print(f"'{c['text']}' x0={c['x0']:.1f} top={c['top']:.1f}")
pdf.close()
