import pathlib
from io import BytesIO
from typing import List

import pytest

from navel import initialization, parsing


@pytest.mark.parametrize(
    "test_dirs",
    (
        [],
        ["test"],
        ["test", "tests"],
    ),
)
def test_generate_config_parseable(test_dirs: List[str]):
    """
    Ensure configuration produced by generate_config is parseable
    """
    test_dirs_paths: List[pathlib.Path] = [pathlib.Path(p) for p in test_dirs]

    config = initialization.generate_config(test_dirs_paths)
    stream = BytesIO()
    stream.write(config.encode("utf-8"))
    stream.seek(0)
    assert parsing.load_config(stream)
