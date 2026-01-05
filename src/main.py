"""PDF to Markdown コンバーター CLIエントリーポイント。

PDFファイルをMarkdown形式に変換するコマンドラインツール。
"""

import argparse
import sys
from pathlib import Path

from .converter import convert_pdf, save_result
from .models import ConvertOptions


def parse_args(args=None):
    """コマンドライン引数をパースする。

    Args:
        args: 引数リスト（Noneの場合はsys.argvを使用）

    Returns:
        パースされた引数のNamespace
    """
    parser = argparse.ArgumentParser(
        prog='pdf2md',
        description='PDFファイルをMarkdown形式に変換します。',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  # ページ単位出力（デフォルト）
  python -m src.main input.pdf -o output/
  
  # 単一ファイル出力
  python -m src.main input.pdf -o output/ --single
  
  # 出力ファイル名を指定
  python -m src.main input.pdf -o output/ --single --name merged
  
  # 画像も抽出
  python -m src.main input.pdf -o output/ --images
'''
    )

    parser.add_argument(
        'pdf_path',
        type=str,
        help='変換するPDFファイルのパス'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='./output',
        help='出力ディレクトリ（デフォルト: ./output）'
    )

    parser.add_argument(
        '-s', '--single',
        action='store_true',
        help='全ページを単一のMarkdownファイルに出力'
    )

    parser.add_argument(
        '-n', '--name',
        type=str,
        default=None,
        help='出力ファイル名のプレフィックス（デフォルト: PDFファイル名）'
    )

    parser.add_argument(
        '--strategy',
        type=str,
        choices=['lines', 'text'],
        default='text',
        help='表抽出の水平戦略（デフォルト: text）'
    )

    parser.add_argument(
        '-i', '--images',
        action='store_true',
        help='PDFから画像を抽出してimages/ディレクトリに保存'
    )

    return parser.parse_args(args)


def main(args=None):
    """メイン処理を実行する。

    Args:
        args: コマンドライン引数（テスト用）

    Returns:
        終了コード（0: 成功, 1: エラー）
    """
    parsed = parse_args(args)

    # PDFファイルの存在確認
    pdf_path = Path(parsed.pdf_path)
    if not pdf_path.exists():
        print(f"エラー: ファイルが見つかりません: {pdf_path}", file=sys.stderr)
        return 1

    if not pdf_path.suffix.lower() == '.pdf':
        print(f"エラー: PDFファイルを指定してください: {pdf_path}", file=sys.stderr)
        return 1

    # 変換オプションの設定
    options = ConvertOptions(
        output_mode="single" if parsed.single else "per_page",
        horizontal_strategy=parsed.strategy,
        extract_images=parsed.images
    )

    try:
        print(f"変換中: {pdf_path}")
        result = convert_pdf(pdf_path, options, output_dir=parsed.output)

        print(f"総ページ数: {len(result.pages)}")

        created_files = save_result(
            result,
            parsed.output,
            options,
            file_prefix=parsed.name
        )

        print(f"\n変換完了: {len(created_files)} ファイル作成")
        return 0

    except Exception as e:
        print(f"エラー: 変換中にエラーが発生しました: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
