import unittest.mock

import pytest
import yaml

from navel.errors import ExprError, NavelError
from navel.models import Settings
from navel.parsing import Rule, parse_rule
from navel.yaml_expr.glob import GlobExpr
from navel.yaml_expr.regex import RegExExpr
from navel.yaml_expr.settings import SettingsExpr as SettingExpr
from navel.yaml_expr.xpath import XPathExpr

GlobExpr.add_to_yaml()
RegExExpr.add_to_yaml()
SettingExpr.add_to_yaml()
XPathExpr.add_to_yaml()


def get_mocket_settings(settings: Settings):
    settings_expr = unittest.mock.MagicMock(spec=SettingExpr)
    settings_expr.settings = settings
    return settings_expr


def get_mocked_xpath(xpath: str):
    loader = unittest.mock.MagicMock()
    loader.construct_scalar = lambda _: xpath
    node = yaml.ScalarNode(tag="!xpath", value=xpath)
    return XPathExpr(loader, node)


@pytest.mark.parametrize(
    "expression,expected_type",
    (
        ("!xpath //*", XPathExpr),
        ("//*", XPathExpr),
        pytest.param("//[]", XPathExpr, marks=pytest.mark.xfail(raises=ExprError)),
        ("!regex .*", RegExExpr),
        pytest.param('!regex "*"', RegExExpr, marks=pytest.mark.xfail(raises=ExprError)),
        ("!settings {included: [], excluded: [], allow_ignore: yes}", SettingExpr),
        pytest.param("!settings {}", SettingExpr, marks=pytest.mark.xfail(raises=ExprError)),
    ),
)
def test_constructors(expression, expected_type):
    """
    Ensure custom YAML expression constructors successfully parse given expressions
    """
    assert isinstance(yaml.load(expression, Loader=yaml.FullLoader), expected_type)


def test_parse_rule():
    """
    Ensure parse_rule returns expected output
    """
    expr = get_mocked_xpath("//Assign/value[Constant]")
    settings1 = get_mocket_settings(Settings(included=[], excluded=[], allow_ignore=True))

    assert parse_rule(
        rule_name="",
        rule_values=dict(
            description="",
            expr=expr,
            example="a = 1",
            instead="a = int('1')",
            settings=settings1,
        ),
    ) == Rule(
        name="",
        description="",
        expr=expr,
        example="a = 1",
        instead="a = int('1')",
        settings=Settings(included=[], excluded=[], allow_ignore=True),
    )


def test_parse_rule_requires_settings():
    """
    Ensure parse_rule raises an exception if settings are not provided
    """
    expr = get_mocked_xpath("//Constant")

    with pytest.raises(NavelError):
        parse_rule(
            rule_name="",
            rule_values=dict(
                description="",
                expr=expr,
                example="a = 1",
                instead="a = int('1')",
            ),
        )


@pytest.mark.parametrize(
    "kwargs",
    (
        dict(example="a = "),
        dict(instead="a = int('1'"),
    ),
)
def test_parse_rule_validates_code_examples(kwargs):
    """
    Ensure parse_rule raises an exception if code examples are syntactically invalid
    """

    expr = get_mocked_xpath("//Constant")

    with pytest.raises(NavelError):
        parse_rule(rule_name="", rule_values=dict(description="", expr=expr, **kwargs))
