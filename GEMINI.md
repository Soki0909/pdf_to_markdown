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
- **models.py**: `ConvertOptions`, `PageContent`, `ConvertResult`データクラス
- **main.py**: argparseを使用したCLIインターフェース

## 開発コマンド

```bash
# テスト実行（ページ単位）
python -m src.main test.pdf -o output/

# テスト実行（単一ファイル）
python -m src.main test.pdf -o output/ --single --name merged

# テスト実行（画像抽出付き）
python -m src.main test.pdf -o output/ --images
```

## 将来の拡張予定

1. **Webアプリ化**: FastAPIでPDFアップロード→zip形式でダウンロード
2. **バッチ処理**: 複数PDFの一括変換

