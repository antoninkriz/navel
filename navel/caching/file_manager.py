"""
Module handling files and their caching
"""

import ast
import dataclasses
import pathlib
import tokenize
from typing import Dict, List

import lxml.etree
import pyastgrep.asts
import pyastgrep.files


@dataclasses.dataclass
class File:
    """
    Class caching opened and parsed file
    """

    def __init__(self, file_bin: bytes, file_name: str):
        file_str, file_ast = pyastgrep.files.parse_python_file(file_bin, file_name, auto_dedent=False)
        ast_xml_mapping: Dict[lxml.etree._Element, ast.AST] = {}
        file_xml = pyastgrep.asts.ast_to_xml(file_ast, ast_xml_mapping)
        lines = iter(file_str.splitlines(True))
        file_tkn = list(tokenize.generate_tokens(lambda: next(lines)))

        self.ast: ast.AST = file_ast
        self.xml: lxml.etree._Element = file_xml
        self.ast_xml_mapping: Dict[lxml.etree._Element, ast.AST] = ast_xml_mapping
        self.content_bytes: bytes = file_bin
        self.content_str: str = file_str
        self.tokens: List[tokenize.TokenInfo] = file_tkn


class FileManager:
    """
    Class caching all files that have been read and parsed
    """

    def __init__(self) -> None:
        self._files: Dict[pathlib.Path, File] = {}

    def get(self, path: pathlib.Path) -> File:
        """
        Get File object from the cache or read it if not present
        @param path: Path to the file
        @return: Cached file object
        """
        try:
            return self._files[path]
        except KeyError:
            self._files[path] = File(path.read_bytes(), path.name)
            return self._files[path]
