"""PDF to Markdown変換モジュール。

pdfplumberを使用してPDFからテキストと表を抽出し、
Markdown形式に変換する機能を提供する。
"""

import io
import os
from operator import itemgetter
from pathlib import Path
from typing import List, Dict, Any, Union

import pdfplumber
from PIL import Image

from .models import ConvertOptions, PageContent, ConvertResult


def deduplicate_page(page):
    """同じ位置にある重複文字を除去したページを返す。

    一部のPDFでは装飾効果（影やアウトライン）のために
    同じ位置に同じ文字が複数配置されている。
    位置情報（x0, top）を基に重複を検出・除去する。

    この方法では正当な連続文字（「第11編」など）は影響を受けない。

    Args:
        page: pdfplumberのPageオブジェクト

    Returns:
        重複文字を除去したPageオブジェクト
    """
    if not page.chars:
        return page

    # 位置ベースで重複を検出し、ユニークな文字のインデックスを記録
    seen_positions = set()
    indices_to_keep = set()

    for i, char in enumerate(page.chars):
        # 位置と文字内容でキーを作成（小数点以下1桁で丸める）
        key = (
            round(char['x0'], 1),
            round(char['top'], 1),
            char['text']
        )
        if key not in seen_positions:
            seen_positions.add(key)
            indices_to_keep.add(i)

    # 重複がある場合のみフィルタリング
    if len(indices_to_keep) < len(page.chars):
        # 各charオブジェクトのid()をインデックスにマッピング
        char_index_map = {id(char): i for i, char in enumerate(page.chars)}

        def keep_object(obj):
            # 文字オブジェクト以外は保持
            if obj.get('object_type') != 'char':
                return True
            # このオブジェクトのインデックスを取得してチェック
            char_id = id(obj)
            if char_id in char_index_map:
                return char_index_map[char_id] in indices_to_keep
            return True

        return page.filter(keep_object)

    return page


def extract_contents(page, horizontal_strategy: str = "text") -> List[Dict[str, Any]]:
    """PDFページから重複しないテキストおよび表データを抽出する。

    Args:
        page: pdfplumberのPageオブジェクト
        horizontal_strategy: 表抽出の水平戦略（"lines"または"text"）

    Returns:
        抽出したコンテンツのリスト。各要素は'top'キーと
        'text'または'table'キーを持つ辞書
    """
    # 重複文字を位置ベースで除去
    page = deduplicate_page(page)

    contents = []
    table_settings = {"horizontal_strategy": horizontal_strategy}

    # テーブル抽出を試行
    try:
        tables = page.find_tables(table_settings=table_settings)
    except Exception as e:
        print(f"Warning: Table extraction failed: {e}")
        tables = []

    # テーブルに含まれないすべてのテキストデータを抽出
    non_table_content = page
    for table in tables:
        try:
            non_table_content = non_table_content.outside_bbox(table.bbox)
        except Exception:
            continue

    try:
        for line in non_table_content.extract_text_lines():
            contents.append({'top': line['top'], 'text': line['text']})
    except Exception as e:
        print(f"Warning: Text extraction failed: {e}")

    # すべての表データを抽出
    for table in tables:
        try:
            contents.append({'top': table.bbox[1], 'table': table})
        except Exception:
            continue

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


def extract_images(
    page,
    page_number: int,
    output_dir: Path,
    file_prefix: str
) -> List[str]:
    """PDFページから画像を抽出して保存する。

    Args:
        page: pdfplumberのPageオブジェクト
        page_number: ページ番号
        output_dir: 画像出力ディレクトリ
        file_prefix: ファイル名プレフィックス

    Returns:
        保存された画像ファイルパスのリスト
    """
    saved_images = []
    images = page.images

    if not images:
        return saved_images

    # 画像出力ディレクトリを作成
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    for idx, img in enumerate(images, start=1):
        try:
            # pdfplumberの画像情報から画像を抽出
            # 画像のバウンディングボックスを取得
            x0, top, x1, bottom = img['x0'], img['top'], img['x1'], img['bottom']

            # ページ境界を取得
            page_width = page.width
            page_height = page.height

            # bboxをページ境界内にクリップ
            x0 = max(0, min(x0, page_width))
            x1 = max(0, min(x1, page_width))
            top = max(0, min(top, page_height))
            bottom = max(0, min(bottom, page_height))

            # 有効な領域かチェック（幅・高さが0以上）
            if x1 <= x0 or bottom <= top:
                continue

            # ページから画像領域をクロップ
            cropped = page.within_bbox((x0, top, x1, bottom))
            if cropped:
                # ページを画像としてレンダリング
                pil_image = cropped.to_image(resolution=150).original

                # ファイル名を生成
                filename = f"{file_prefix}_page{page_number}_img{idx}.png"
                filepath = images_dir / filename

                # 画像を保存
                pil_image.save(filepath, "PNG")
                saved_images.append(str(filepath))
                print(f"Extracted: {filepath}")

        except Exception as e:
            print(
                f"Warning: Failed to extract image {idx} on page {page_number}: {e}")
            continue

    return saved_images


def convert_pdf(
    pdf_path: Union[str, Path],
    options: ConvertOptions = None,
    output_dir: Union[str, Path] = None
) -> ConvertResult:
    """PDFファイルをMarkdownに変換する。

    Args:
        pdf_path: PDFファイルのパス
        options: 変換オプション（Noneの場合はデフォルト値を使用）
        output_dir: 画像出力ディレクトリ（extract_images有効時に必要）

    Returns:
        変換結果を含むConvertResultオブジェクト
    """
    if options is None:
        options = ConvertOptions()

    pdf_path = Path(pdf_path)
    result = ConvertResult(source_filename=pdf_path.stem)

    # 画像抽出が有効な場合、出力ディレクトリが必要
    if options.extract_images and output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            contents = extract_contents(page, options.horizontal_strategy)
            markdown = convert_contents_to_markdown(contents)

            # 画像抽出
            images = []
            if options.extract_images and output_dir:
                images = extract_images(
                    page, i, output_dir, pdf_path.stem
                )
                # Markdownに画像参照を追加
                if images:
                    image_refs = []
                    for img_path in images:
                        img_name = Path(img_path).name
                        image_refs.append(f"![{img_name}](images/{img_name})")
                    markdown += "\n\n" + "\n\n".join(image_refs)

            result.pages.append(PageContent(
                page_number=i, markdown=markdown, images=images
            ))

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
