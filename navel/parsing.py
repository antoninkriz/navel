import ast
import pathlib

import yaml

from navel.caching.file_manager import File
from navel.errors import ParsingError
from navel.models import Settings, Rule
from navel.yaml_expr.yaml_expr import YamlExpr
from navel.yaml_expr.settings import Settings as SettingsExpr


def validate_syntax(rule_clause):
    try:
        ast.parse(rule_clause)
        return True
    except SyntaxError:
        return False


def matches_expr(yaml_expr: YamlExpr, expr: str) -> bool:
    return len(yaml_expr.match_line_numbers(File(expr.encode('utf-8'), '<settings>'))) != 0


def parse_rule(rule_name, rule_values, default_settings=None):
    rule_description = rule_values.get('description')
    if rule_description is None:
        raise ParsingError(f'Rule "{rule_name}": missing `description`')

    rule_expr = rule_values.get('expr')
    if rule_expr is None:
        raise ParsingError(f'Rule "{rule_name}": missing `expr`')
    if not isinstance(rule_expr, YamlExpr):
        raise ParsingError(f'Rule "{rule_name}": `expr` must be a valid matching expression')

    rule_example = rule_values.get('example')
    if rule_example is not None:
        if validate_syntax(rule_example):
            raise ParsingError(f'Rule "{rule_name}": Invalid syntax in `example` clause')
        if not matches_expr(rule_expr, rule_example):
            raise ParsingError(f'Rule "{rule_name}": `example` is not matched by `expr`')

    rule_instead = rule_values.get('instead')
    if rule_instead is not None:
        if validate_syntax(rule_example):
            raise ParsingError(f'Rule "{rule_name}": Invalid syntax in `instead` clause')
        if matches_expr(rule_expr, rule_example):
            raise ParsingError(f'Rule "{rule_name}": `instead` is matched by `expr`')

    rule_settings = rule_values.get('settings', default_settings)
    if rule_settings is None:
        raise ParsingError(f'Rule "{rule_name}": No `settings` or `default_settings` specified')
    if not isinstance(rule_settings, SettingsExpr):
        raise ParsingError(f'Rule "{rule_name}": `settings` must be a !settings node')

    return Rule(
        name=rule_name,
        description=rule_description,
        expr=rule_expr,
        example=rule_example,
        instead=rule_instead,
        settings=rule_settings.settings,
    )


def load_config(path: pathlib.Path):
    yml = yaml.load(path.open('r'), Loader=yaml.FullLoader)
    rule_settings = yml.get('default_settings')
    if not isinstance(rule_settings, Settings):
        raise ParsingError(f'Value of `default_settings` must be a !settings node')
    rules = [
        parse_rule(rule_name, rule_values, rule_settings)
        for rule_name, rule_values in
        yml.get('rules', {}).items()
    ]
    return rules
