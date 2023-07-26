from typing import List, Tuple, Generator
import pathlib
import re
import tokenize

from navel.caching.file_manager import FileManager, File
from navel.errors import LinterError
from navel.models import Rule
from navel.yaml_expr.yaml_expr import YamlExpr

IGNORE_COMMENTS = [
    re.compile(r'^#\s?bb:\s?ignore$'),
    re.compile(r'^#\s?navel:\s?ignore$'),
]


class Linter:
    def __init__(self, file_manager: FileManager, rules: List[Rule]):
        self._file_manager: FileManager = file_manager
        self._rules: List[Rule] = rules

    @staticmethod
    def _get_ignored_lines(file: File):
        return frozenset(
            line
            for token_type, token, (line, _), _, _ in file.tokens
            if token_type is tokenize.COMMENT
            if any(r.search(token) for r in IGNORE_COMMENTS)
        )

    def lint_file(self, path: pathlib.Path) -> Generator[Tuple[Rule, int]]:
        matching_rules = [
            rule
            for rule in self._rules
            if rule.match_path(path)
        ]
        if len(matching_rules) == 0:
            return

        file = self._file_manager.get(path)
        ignored_lines = self._get_ignored_lines(file)

        for rule in sorted(self._rules, key=lambda x: x.name):
            if not isinstance(rule.expr, YamlExpr):
                raise LinterError(f'Rule {rule.name} is not a valid Navel rule')

            matching_lines = rule.expr.match_line_numbers(file)
            if rule.settings.allow_ignore:
                matching_lines -= ignored_lines

            for line in matching_lines:
                yield rule, line
