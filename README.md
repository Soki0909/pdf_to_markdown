# PDF to Markdown Converter

PDFファイルをMarkdown形式に変換するCLIツールです。  
`pdfplumber`を使用して、テキストと表を構造を保持したまま抽出します。

## 特徴

- **テキスト抽出**: PDFからテキストコンテンツを抽出
- **表のMarkdown変換**: PDF内の表をMarkdownテーブル形式に変換
- **2つの出力モード**:
  - ページ単位出力: 各ページを個別のMarkdownファイルとして出力
  - 単一ファイル出力: 全ページを1つのMarkdownファイルに結合

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な使い方（ページ単位出力）

```bash
python -m src.main input.pdf -o output/
```

これにより、`output/`ディレクトリに`input_page_1.md`、`input_page_2.md`...のようなファイルが作成されます。

### 単一ファイル出力

```bash
python -m src.main input.pdf -o output/ --single
```

これにより、`output/input.md`として全ページが1つのファイルに結合されます。

### オプション一覧

| オプション | 短縮 | 説明 | デフォルト |
|------------|------|------|------------|
| `--output` | `-o` | 出力ディレクトリ | `./output` |
| `--single` | `-s` | 単一ファイル出力 | `False` |
| `--name` | `-n` | 出力ファイル名プレフィックス | PDFファイル名 |
| `--strategy` | | 表抽出戦略（`lines`/`text`） | `text` |

### 例

```bash
# 出力ファイル名を指定
python -m src.main input.pdf -o output/ --single --name merged

# 表抽出戦略を変更
python -m src.main input.pdf -o output/ --strategy lines
```

## プログラムからの使用

```python
from src.converter import convert_pdf, save_result
from src.models import ConvertOptions

# PDFを変換
options = ConvertOptions(output_mode="single")
result = convert_pdf("input.pdf", options)

# 結果を保存
save_result(result, "output/", options)

# または直接Markdown文字列を取得
markdown_text = result.to_single_markdown()
```

## 出力形式

### ページ単位出力
各ファイルの先頭にページ番号がヘッダーとして追加されます：
```markdown
# Page 1

（コンテンツ）
```

### 単一ファイル出力
ページ間は水平線で区切られます：
```markdown
## Page 1

（コンテンツ）

---
## Page 2

（コンテンツ）
```

## 参考

- [pdfplumber](https://github.com/jsvine/pdfplumber)
- [RAG用にPDFをMarkdownに変換する（Qiita）](https://qiita.com/vko/items/04fb0756abd89dff8573)
