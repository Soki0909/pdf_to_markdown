# PDF to Markdown Converter

pdfplumberを使用してPDFをMarkdown形式に変換するCLIツール。

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
├── README.md             # ユーザー向けドキュメント
└── GEMINI.md             # 開発者向けコンテキスト
```

## アーキテクチャ

- **converter.py**: コアモジュール。CLIとWebアプリの両方から利用可能
  - `deduplicate_page()`: 装飾効果で重複配置された文字を位置情報(x0, top)に基づき除去
  - `find_pdf_files()`: ディレクトリ内のPDFファイルを再帰的に検索
  - `convert_directory()`: ディレクトリ構造を保持したまま全PDFを一括変換
- **models.py**: `ConvertOptions`, `PageContent`, `ConvertResult`データクラス
- **main.py**: argparseを使用したCLIインターフェース、ファイル/ディレクトリ自動判定

## 開発コマンド

```bash
# 単一ファイル変換（ページ単位）
python -m src.main test.pdf -o output/

# 単一ファイル変換（単一ファイル）
python -m src.main test.pdf -o output/ --single --name merged

# 単一ファイル変換（画像抽出付き）
python -m src.main test.pdf -o output/ --images

# ディレクトリ一括変換（ページ単位）
python -m src.main ./pdf_folder -o output/

# ディレクトリ一括変換（単一ファイル）
python -m src.main ./pdf_folder -o output/ --single

# ディレクトリ一括変換（画像抽出付き）
python -m src.main ./pdf_folder -o output/ --images
```

## 将来の拡張予定

1. **Webアプリ化**: FastAPIでPDFアップロード→zip形式でダウンロード
2. **バッチ処理**: 複数PDFの一括変換

