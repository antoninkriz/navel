from typing import List, Dict

import ast
import dataclasses
import pathlib
import tokenize

import lxml.etree
import pyastgrep.asts
import pyastgrep.files


class File:
    def __init__(self, file_bin: bytes, file_name: str):
        file_str, file_ast = pyastgrep.files.parse_python_file(file_bin, file_name, auto_dedent=False)
        ast_xml_mapping = {}
        file_xml = pyastgrep.asts.ast_to_xml(file_ast, ast_xml_mapping)
        lines = file_str.splitlines(True)
        file_tkn = list(tokenize.generate_tokens(lambda: next(iter(lines))))

        self.ast: ast.AST = file_ast
        self.xml: lxml.etree._Element = file_xml
        self.ast_xml_mapping: Dict[lxml.etree._Element, ast.AST] = ast_xml_mapping
        self.content_bytes: bytes = file_bin
        self.content_str: str = file_str
        self.tokens: List[tokenize.TokenInfo] = file_tkn


class FileManager:
    def __init__(self):
        self._files: dict[pathlib.Path, File] = dict()

    def get(self, path: pathlib.Path) -> File:
        try:
            return self._files[path]
        except KeyError:
            self._files[path] = File(path.read_bytes(), path.name)
            return self._files[path]
