import re
from typing import List

import lxml.etree
import pyastgrep.search
import yaml

from navel.caching.file_manager import File
from navel.errors import ExprError
from navel.yaml_expr.yaml_expr import YamlExpr, yaml_add


@yaml_add
class XPathExpr(YamlExpr):
    """
    Construct and parse XPath expressions in YAML

    YAML:
    !xpath //*
    Output:
    lxml.etree.XPath(//*)

    or

    YAML:
    //*
    Output:
    lxml.etree.XPath(//*)
    """

    PATTERN = re.compile(r"/.+")

    def __init__(self, loader: yaml.Loader, node: yaml.ScalarNode):
        super().__init__(loader, node)
        val = loader.construct_scalar(node)
        if not isinstance(val, str):
            raise ExprError("Invalid XPath")
        try:
            self._path = lxml.etree.XPath(val)
        except lxml.etree.XPathSyntaxError as exc:
            raise ExprError("Invalid XPath") from exc

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._path}>"

    def match_line_numbers(self, file: File) -> List[int]:
        matching_elements = self._path(file.xml)

        if not isinstance(matching_elements, list):
            raise ExprError(f"Result not iterable: {str(matching_elements)}")
        iterator = iter(matching_elements)

        linenos = []
        for element in iterator:
            if not isinstance(element, lxml.etree._Element):
                raise ExprError(f"Not an AST node: {str(element)}")

            ast_node = file.ast_xml_mapping.get(element, None)
            if ast_node is not None:
                position = pyastgrep.search.position_from_node(ast_node)
                if position is not None:
                    linenos.append(position.lineno)
        return linenos

    def matches(self, file: File) -> bool:
        return bool(self._path(file.xml))
