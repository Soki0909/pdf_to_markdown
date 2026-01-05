"""データクラス定義モジュール。

変換オプションと結果を表すデータ構造を定義する。
"""

from dataclasses import dataclass, field
from typing import List, Literal


@dataclass
class ConvertOptions:
    """PDF変換オプションを保持するデータクラス。

    Attributes:
        output_mode: 出力モード。"per_page"でページ単位、"single"で単一ファイル
        horizontal_strategy: pdfplumberのtable抽出戦略。"lines"または"text"
        page_separator: 単一ファイル出力時のページ区切り文字列
        extract_images: 画像を抽出するかどうか
    """
    output_mode: Literal["per_page", "single"] = "per_page"
    horizontal_strategy: Literal["lines", "text"] = "text"
    page_separator: str = "\n---\n"
    extract_images: bool = False


@dataclass
class PageContent:
    """1ページ分の変換結果を保持するデータクラス。

    Attributes:
        page_number: ページ番号（1始まり）
        markdown: Markdown形式に変換されたコンテンツ
        images: 抽出された画像ファイルパスのリスト
    """
    page_number: int
    markdown: str
    images: List[str] = field(default_factory=list)


@dataclass
class ConvertResult:
    """PDF全体の変換結果を保持するデータクラス。

    Attributes:
        pages: 各ページの変換結果リスト
        source_filename: 元のPDFファイル名
    """
    pages: List[PageContent] = field(default_factory=list)
    source_filename: str = ""

    def to_single_markdown(self, page_separator: str = "\n---\n") -> str:
        """全ページを単一のMarkdown文字列に結合する。

        Args:
            page_separator: ページ間の区切り文字列

        Returns:
            結合されたMarkdown文字列
        """
        parts = []
        for page in self.pages:
            parts.append(f"## Page {page.page_number}\n\n{page.markdown}")
        return page_separator.join(parts)
