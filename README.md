# PDF to Markdown Converter

PDFファイルをMarkdown形式に変換するCLIツールです。  
`pdfplumber`を使用して、テキストと表を構造を保持したまま抽出します。

## 特徴

- **テキスト抽出**: PDFからテキストコンテンツを正確に抽出
- **表のMarkdown変換**: PDF内の表をMarkdownテーブル形式に自動変換
- **画像抽出**: PDF内の画像をPNG形式で抽出（オプション）
- **重複文字の自動除去**: 装飾効果で重複配置された文字を位置情報に基づき自動除去
- **ディレクトリ一括変換**: フォルダ構造を保持したまま複数のPDFを一括処理
- **2つの出力モード**:
  - **ページ単位出力**: 各ページを個別のMarkdownファイルとして出力
  - **単一ファイル出力**: 全ページを1つのMarkdownファイルに結合

## インストール

### 必要な環境
- Python 3.7以降

### 手順

1. このリポジトリをクローンまたはダウンロード
2. 必要なパッケージをインストール:

```bash
pip install -r requirements.txt
```

## 使い方

### 基本的な使い方

#### 1. 単一PDFファイルの変換（ページ単位出力）

PDFファイルを指定して、各ページを個別のMarkdownファイルとして出力します。

```bash
python -m src.main input.pdf -o output/
```

**出力例:**
```
output/
├── input_page_1.md
├── input_page_2.md
├── input_page_3.md
└── ...
```

#### 2. 単一PDFファイルの変換（単一ファイル出力）

全ページを1つのMarkdownファイルにまとめて出力します。

```bash
python -m src.main input.pdf -o output/ --single
```

**出力例:**
```
output/
└── input.md  （全ページを含む1つのファイル）
```

#### 3. ディレクトリ一括変換

フォルダ内の全PDFファイルを一括変換します。サブフォルダ内のPDFも自動検出され、フォルダ構造がそのまま保持されます。

```bash
python -m src.main ./pdf_folder -o output/
```

**入力例:**
```
pdf_folder/
├── report1.pdf
├── subfolder/
│   ├── report2.pdf
│   └── report3.pdf
```

**出力例（ページ単位モード）:**
```
output/
├── report1/
│   ├── report1_page_1.md
│   ├── report1_page_2.md
│   └── ...
├── subfolder/
│   ├── report2/
│   │   ├── report2_page_1.md
│   │   └── ...
│   └── report3/
│       └── ...
```

**出力例（単一ファイルモード）:**
```
output/
├── report1.md
└── subfolder/
    ├── report2.md
    └── report3.md
```

#### 4. 画像抽出付き変換

PDFから画像も抽出して保存します。

```bash
python -m src.main input.pdf -o output/ --images
```

**出力例:**
```
output/
├── input_page_1.md
├── input_page_2.md
└── images/
    ├── input_page1_img1.png
    ├── input_page2_img1.png
    └── ...
```

### オプション一覧

| オプション | 短縮 | 説明 | デフォルト |
|------------|------|------|------------|
| `--output` | `-o` | 出力ディレクトリ | `./output` |
| `--single` | `-s` | 単一ファイル出力（全ページを1つのファイルに結合） | `False` |
| `--name` | `-n` | 出力ファイル名プレフィックス | PDFファイル名 |
| `--images` | `-i` | 画像を抽出して保存 | `False` |
| `--strategy` | | 表抽出戦略（`lines` または `text`） | `text` |

### 詳細な使用例

```bash
# 出力ファイル名を指定
python -m src.main input.pdf -o output/ --single --name merged

# ディレクトリを単一ファイルモードで変換
python -m src.main ./pdf_folder -o output/ --single

# ディレクトリを画像抽出付きで変換
python -m src.main ./pdf_folder -o output/ --images

# 単一ファイルモード + 画像抽出
python -m src.main input.pdf -o output/ --single --images

# 表抽出戦略を変更
python -m src.main input.pdf -o output/ --strategy lines
```

### よくある使い方

#### 📄 レポートや論文を変換したい
```bash
# ページ単位で管理しやすく
python -m src.main report.pdf -o output/
```

#### 📚 複数の資料をまとめて変換したい
```bash
# フォルダごと一括変換
python -m src.main ./documents -o converted/
```

#### 🖼️ 図表も含めて保存したい
```bash
# 画像も一緒に抽出
python -m src.main document.pdf -o output/ --images
```

#### 📝 全ページを1つのファイルにまとめたい
```bash
# 単一ファイルとして出力
python -m src.main document.pdf -o output/ --single
```

## プログラムからの使用

Pythonスクリプト内で直接利用することもできます。

### 単一ファイルの変換

```python
from src.converter import convert_pdf, save_result
from src.models import ConvertOptions

# PDFを変換
options = ConvertOptions(output_mode="single", extract_images=True)
result = convert_pdf("input.pdf", options, output_dir="output/")

# 結果を保存
save_result(result, "output/", options)

# または直接Markdown文字列を取得
markdown_text = result.to_single_markdown()
print(markdown_text)
```

### ディレクトリの一括変換

```python
from src.converter import convert_directory
from src.models import ConvertOptions

# ディレクトリを変換
options = ConvertOptions(output_mode="per_page")
result = convert_directory("./pdf_folder", "output/", options)

# 統計情報を表示
print(f"総PDFファイル数: {result['total']}")
print(f"成功: {result['success']}")
print(f"失敗: {result['failed']}")
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

### 画像抽出
画像は`images/`サブディレクトリに保存され、Markdownファイル内に参照が自動挿入されます：
```markdown
![image_name.png](images/image_name.png)
```

## トラブルシューティング

### PDFファイルが見つからないと表示される
- ファイルパスが正しいか確認してください
- 相対パスではなく絶対パスを試してみてください

### 一部の文字が重複して表示される
- このツールは自動的に重複文字を除去しますが、一部のPDFでは完全には対処できない場合があります

### 表が正しく抽出されない
- `--strategy lines`オプションを試してください
- PDFによっては表構造が認識されない場合があります

## プロジェクト構成

```
pdf_to_markdown/
├── src/
│   ├── __init__.py       # パッケージ初期化
│   ├── main.py           # CLIエントリーポイント
│   ├── converter.py      # 変換ロジック（コアモジュール）
│   └── models.py         # データクラス定義
├── output/               # デフォルト出力先
├── requirements.txt      # 依存関係
└── README.md             # このファイル
```

## 参考

- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF解析ライブラリ
- [RAG用にPDFをMarkdownに変換する（Qiita）](https://qiita.com/vko/items/04fb0756abd89dff8573)

## ライセンス

このプロジェクトはオープンソースです。

## 今後の拡張予定

- Webアプリ化（FastAPIでPDFアップロード→zip形式でダウンロード）
- バッチ処理の最適化
- より多様なPDF形式への対応
