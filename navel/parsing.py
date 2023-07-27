import ast
import pathlib
from typing import Any, Dict, List, Optional, TextIO

import yaml

from navel.caching.file_manager import File
from navel.errors import ParsingError
from navel.models import Rule
from navel.yaml_expr.glob import GlobExpr
from navel.yaml_expr.regex import RegExExpr
from navel.yaml_expr.settings import SettingsExpr
from navel.yaml_expr.xpath import XPathExpr
from navel.yaml_expr.yaml_expr import YamlExpr

GlobExpr.add_to_yaml()
RegExExpr.add_to_yaml()
SettingsExpr.add_to_yaml()
XPathExpr.add_to_yaml()


def validate_syntax(rule_clause: str) -> bool:
    try:
        ast.parse(rule_clause)
        return True
    except SyntaxError:
        return False


def matches_expr(yaml_expr: YamlExpr, expr: str) -> bool:
    return yaml_expr.matches(File(expr.encode("utf-8"), "<settings>"))


def parse_rule(
    rule_name: str,
    rule_values: Dict[str, Any],
    default_settings: Optional[SettingsExpr] = None,
) -> Rule:
    description = rule_values.get("description")
    if description is None:
        raise ParsingError(f'Rule "{rule_name}": missing `description`')

    expr = rule_values.get("expr")
    if expr is None:
        raise ParsingError(f'Rule "{rule_name}": missing `expr`')
    if not isinstance(expr, YamlExpr):
        raise ParsingError(f'Rule "{rule_name}": `expr` must be a valid matching expression')

    example = rule_values.get("example")
    if example is not None:
        if not validate_syntax(example):
            raise ParsingError(f'Rule "{rule_name}": Invalid syntax in `example` clause {example}')
        if not matches_expr(expr, example):
            raise ParsingError(f'Rule "{rule_name}": `example` is not matched by `expr`')

    instead = rule_values.get("instead")
    if instead is not None:
        if not validate_syntax(instead):
            raise ParsingError(f'Rule "{rule_name}": Invalid syntax in `instead` clause')
        if matches_expr(expr, instead):
            raise ParsingError(f'Rule "{rule_name}": `instead` is matched by `expr`')

    settings = rule_values.get("settings", default_settings)
    if settings is None:
        raise ParsingError(f'Rule "{rule_name}": No `settings` or `default_settings` specified')
    if not isinstance(settings, SettingsExpr):
        raise ParsingError(f'Rule "{rule_name}": `settings` must be a !settings node')

    return Rule(
        name=rule_name,
        description=description,
        expr=expr,
        example=example,
        instead=instead,
        settings=settings.settings,
    )


def load_config(stream: TextIO) -> List[Rule]:
    yml = yaml.load(stream, Loader=yaml.FullLoader)
    default_settings = yml.get("default_settings")
    if default_settings is not None and not isinstance(default_settings, SettingsExpr):
        raise ParsingError("Value of `default_settings` must be a !settings node.")
    rules = [
        parse_rule(rule_name, rule_values, default_settings) for rule_name, rule_values in yml.get("rules", {}).items()
    ]
    return rules


def load_config_file(path: pathlib.Path) -> List[Rule]:
    return load_config(path.open("r"))
