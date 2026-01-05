"""PDF to Markdown変換モジュール。

pdfplumberを使用してPDFからテキストと表を抽出し、
Markdown形式に変換する機能を提供する。
"""

import os
from operator import itemgetter
from pathlib import Path
from typing import List, Dict, Any, Union

import pdfplumber

from .models import ConvertOptions, PageContent, ConvertResult


def extract_contents(page, horizontal_strategy: str = "text") -> List[Dict[str, Any]]:
    """PDFページから重複しないテキストおよび表データを抽出する。

    Args:
        page: pdfplumberのPageオブジェクト
        horizontal_strategy: 表抽出の水平戦略（"lines"または"text"）

    Returns:
        抽出したコンテンツのリスト。各要素は'top'キーと
        'text'または'table'キーを持つ辞書
    """
    contents = []
    table_settings = {"horizontal_strategy": horizontal_strategy}
    tables = page.find_tables(table_settings=table_settings)

    # テーブルに含まれないすべてのテキストデータを抽出
    non_table_content = page
    for table in tables:
        non_table_content = non_table_content.outside_bbox(table.bbox)

    for line in non_table_content.extract_text_lines():
        contents.append({'top': line['top'], 'text': line['text']})

    # すべての表データを抽出
    for table in tables:
        contents.append({'top': table.bbox[1], 'table': table})

    # 行を上部位置でソート
    contents = sorted(contents, key=itemgetter('top'))

    return contents


def sanitize_cell(cell) -> str:
    """セルの内容を整理する。

    Args:
        cell: セルの内容（文字列またはNone）

    Returns:
        整理された文字列
    """
    if cell is None:
        return ""
    # すべての種類の空白を正規化し、文字列であることを保証
    return ' '.join(str(cell).split())


def convert_table_to_markdown(table) -> str:
    """表オブジェクトをMarkdown形式に変換する。

    Args:
        table: pdfplumberのTableオブジェクト

    Returns:
        Markdown形式の表文字列
    """
    unsanitized_table = table.extract()
    if not unsanitized_table:
        return ""

    sanitized_table = [[sanitize_cell(cell) for cell in row]
                       for row in unsanitized_table]

    lines = []
    for i, row in enumerate(sanitized_table):
        md_row = '| ' + ' | '.join(row) + ' |'
        lines.append(md_row)
        # 最初の行（ヘッダー行）の後にヘッダーセパレーターを追加
        if i == 0:
            header_separator = '|:--' * len(row) + ':|'
            lines.append(header_separator)

    return '\n'.join(lines)


def convert_contents_to_markdown(contents: List[Dict[str, Any]]) -> str:
    """抽出したコンテンツをMarkdown文字列に変換する。

    Args:
        contents: extract_contentsで取得したコンテンツリスト

    Returns:
        Markdown形式の文字列
    """
    parts = []

    for content in contents:
        if 'text' in content:
            # テキスト内容を段落として追加
            parts.append(content['text'])
        elif 'table' in content:
            table_md = convert_table_to_markdown(content['table'])
            if table_md:
                parts.append(table_md)

    return '\n\n'.join(parts)


def convert_pdf(
    pdf_path: Union[str, Path],
    options: ConvertOptions = None
) -> ConvertResult:
    """PDFファイルをMarkdownに変換する。

    Args:
        pdf_path: PDFファイルのパス
        options: 変換オプション（Noneの場合はデフォルト値を使用）

    Returns:
        変換結果を含むConvertResultオブジェクト
    """
    if options is None:
        options = ConvertOptions()

    pdf_path = Path(pdf_path)
    result = ConvertResult(source_filename=pdf_path.stem)

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            contents = extract_contents(page, options.horizontal_strategy)
            markdown = convert_contents_to_markdown(contents)
            result.pages.append(PageContent(page_number=i, markdown=markdown))

    return result


def save_result(
    result: ConvertResult,
    output_dir: Union[str, Path],
    options: ConvertOptions = None,
    file_prefix: str = None
) -> List[Path]:
    """変換結果をファイルに保存する。

    Args:
        result: 変換結果
        output_dir: 出力ディレクトリ
        options: 変換オプション
        file_prefix: ファイル名のプレフィックス（Noneの場合はソースファイル名）

    Returns:
        作成されたファイルのパスリスト
    """
    if options is None:
        options = ConvertOptions()

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    prefix = file_prefix or result.source_filename
    created_files = []

    if options.output_mode == "single":
        # 単一ファイル出力
        filepath = output_dir / f"{prefix}.md"
        content = result.to_single_markdown(options.page_separator)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        created_files.append(filepath)
        print(f"Created: {filepath}")
    else:
        # ページ単位出力
        for page in result.pages:
            filename = f"{prefix}_page_{page.page_number}.md"
            filepath = output_dir / filename
            content = f"# Page {page.page_number}\n\n{page.markdown}"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            created_files.append(filepath)
            print(f"Created: {filepath}")

    return created_files
