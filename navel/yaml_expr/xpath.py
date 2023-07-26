from typing import List

import lxml.etree
import yaml
import pyastgrep.search

from navel.caching.file_manager import File
from navel.errors import ExprError
from navel.yaml_expr.yaml_expr import YamlExpr


class XPath(YamlExpr):
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

    def __init__(self, loader: yaml.Loader, node: yaml.ScalarNode):
        super().__init__(loader, node)
        self._path = lxml.etree.XPath(
            loader.construct_scalar(node)
        )

    def match_line_numbers(self, file: File) -> List[int]:
        matching_elements = file.xml.xpath(self._path)

        try:
            iterator = iter(matching_elements)
        except TypeError:
            raise ExprError(f'Result not iterable: {matching_elements}')

        linenos = []
        for element in iterator:
            if not isinstance(element, lxml.etree._Element):
                raise ExprError(f'Not an AST node: {element}')

            ast_node = file.ast_xml_mapping.get(element, None)
            if ast_node is not None:
                position = pyastgrep.search.position_from_node(ast_node)
                if position is not None:
                    linenos.append(position.lineno)
        return linenos
