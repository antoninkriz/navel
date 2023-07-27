import dataclasses
import fnmatch
import pathlib
from typing import List, Union

from navel.yaml_expr.glob import GlobExpr
from navel.yaml_expr.yaml_expr import YamlExpr


@dataclasses.dataclass
class Settings:
    included: List[Union[str, GlobExpr]]
    excluded: List[Union[str, GlobExpr]]
    allow_ignore: bool


@dataclasses.dataclass
class Rule:
    name: str
    description: str
    expr: YamlExpr
    example: str
    instead: str
    settings: Settings

    def match_path(self, path: pathlib.Path) -> bool:
        should_be_included = any(
            fnmatch.fnmatch(str(path), included_pattern.glob if isinstance(included_pattern, GlobExpr) else included_pattern) for included_pattern in self.settings.included
        )
        should_be_excluded = any(
            fnmatch.fnmatch(str(path), excluded_pattern.glob if isinstance(excluded_pattern, GlobExpr) else excluded_pattern) for excluded_pattern in self.settings.excluded
        )
        return should_be_included and not should_be_excluded


@dataclasses.dataclass
class LintingFailure:
    path: pathlib.Path
    lineno: int
    line: str
    rule: Rule
