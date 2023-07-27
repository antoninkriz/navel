import os
import pathlib
import subprocess
import sys
import textwrap
from typing import Generator, Iterable, List, Tuple

import click

from navel.caching.file_manager import FileManager
from navel.errors import NavelError
from navel.initialization import generate_config
from navel.linter import Linter
from navel.models import LintingFailure, Rule
from navel.parsing import load_config_file


@click.group()
def cli() -> None:
    pass


def walk_python_files(root_dir: pathlib.Path) -> Iterable[pathlib.Path]:
    return (
        pathlib.Path(os.path.join(root, file_name))
        for root, _, file_names in os.walk(root_dir)
        for file_name in file_names
        if os.path.splitext(file_name)[-1] == ".py"
    )


def get_git_modified(project_directory: pathlib.Path) -> Iterable[pathlib.Path]:
    default_branch = (
        subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            check=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
        )
        .stdout.strip()
        .split("/")[-1]
    )

    return frozenset(
        pathlib.Path(os.path.abspath(path))
        for diff in ("--staged", f"{default_branch}...")
        for path in subprocess.run(
            ["git", "-C", project_directory, "diff", diff, "--name-only"],
            check=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
        )
        .stdout.strip()
        .splitlines()
        if os.path.splitext(path)[-1] == ".py"
    )


def linting_failures(filepaths: List[pathlib.Path], rules: List[Rule]) -> Generator[LintingFailure, None, None]:
    """Given a set of filepaths and a set of rules, yield all rule violations."""
    failures = 0

    file_manager = FileManager()
    linter = Linter(file_manager, rules)

    for filepath in filepaths:
        linting_results = list(linter.lint_file(filepath))
        if len(linting_results) == 0:
            continue

        file_contents = file_manager.get(filepath).content_str
        for failure in linting_results:
            failures += 1
            lines = file_contents.splitlines()
            yield LintingFailure(
                path=filepath,
                lineno=failure[1],
                line=lines[min(failure[1], len(lines)) - 1] if lines else "",
                rule=failure[0],
            )


@cli.command()
@click.option(
    "--project-directory",
    help="Path to the root directory of the project to be initialized",
    type=click.Path(
        exists=True,
        dir_okay=True,
        file_okay=False,
        writable=True,
        readable=True,
        path_type=pathlib.Path,
    ),
    default=pathlib.Path("."),
)
@click.option(
    "--force",
    help="Force initialize the project",
    is_flag=True,
    default=False,
)
@click.option(
    "--bellybutton",
    help="Initialize .bellybutton.yml file instead of .navel.yml",
    is_flag=True,
    default=False,
)
def init(project_directory: pathlib.Path, force: bool, bellybutton: bool) -> None:
    config_file_bellybutton = project_directory / ".bellybutton.yml"
    config_file_navel = project_directory / ".navel.yml"

    if not force:
        if config_file_bellybutton.exists():
            raise click.ClickException(f"Path `{project_directory}` is already initialized Bellybutton project")

        if config_file_navel.exists():
            raise click.ClickException(f"Path `{project_directory}` is already initialized Navel project")

    config = generate_config(
        pathlib.Path(directory)
        for directory in os.listdir(project_directory)
        if os.path.isdir(os.path.join(project_directory, directory)) and directory.startswith("test")
    )

    if bellybutton:
        config_file_bellybutton.write_text(config)
    else:
        config_file_navel.write_text(config)


@cli.command()
@click.option(
    "--project-directory",
    help="Path to the root directory of the project to be initialized",
    type=click.Path(
        exists=True,
        dir_okay=True,
        file_okay=False,
        writable=True,
        readable=True,
        path_type=pathlib.Path,
    ),
    default=pathlib.Path("."),
)
@click.option(
    "--modified-only",
    help="Check only modified files based on their GIT status",
    is_flag=True,
    default=False,
)
@click.option(
    "--verbose",
    "-v",
    help="Enables verbose output",
    is_flag=True,
    default=False,
)
@click.option("--files", "-f", help="Specifies exact files to be checked", multiple=True, required=False)
def lint(
    project_directory: pathlib.Path,
    modified_only: bool,
    verbose: bool,
    files: Tuple[str],
) -> None:
    config_file_bellybutton = project_directory / ".bellybutton.yml"
    config_file_navel = project_directory / ".navel.yml"

    bellybutton = config_file_bellybutton.exists()
    if not bellybutton and not config_file_navel.exists():
        raise click.ClickException(f"Uninitialized `{project_directory}` - config file not found")

    try:
        rules = load_config_file(config_file_bellybutton if bellybutton else config_file_navel)
    except NavelError as exc:
        raise click.ClickException(repr(exc)) from exc
    except IOError as exc:
        raise click.ClickException(
            f"Can not read from config file `{config_file_bellybutton if bellybutton else config_file_navel}`"
        ) from exc

    filepaths: List[pathlib.Path] = (
        list(get_git_modified(project_directory) if modified_only else walk_python_files(project_directory))
        if len(files) == 0
        else [pathlib.Path(f) for f in files]
    )

    failures = 0
    for failure in linting_failures(filepaths, rules):
        failures += 1
        path = os.path.relpath(failure.path, project_directory)
        lineno = failure.lineno
        line = failure.line
        rule = failure.rule

        if verbose:
            file_name = click.style(f"{path}:{lineno}", fg="bright_magenta", bold=True)
            rule_name = click.style(rule.name, fg="bright_magenta", bold=True, underline=True)
            example = (
                f'{click.style("Example", bold=True)}:\n{rule.example.strip()}\n' if rule.example is not None else ""
            )
            instead = (
                f'{click.style("Instead", bold=True)}:\n{rule.instead.strip()}\n' if rule.instead is not None else ""
            )

            click.echo(
                textwrap.dedent(f"""
                    {file_name}\t{rule_name}
                    {click.style("Description", bold=True)}: {rule.description}
                    {click.style("Line", bold=True)}:
                    {line}
                    {example}{instead}
                """).lstrip()
            )
        else:
            click.echo(f"{path}:{lineno}\t{rule.name}: {rule.description}")

    click.echo(
        click.style(
            f'Linting {"failed" if failures else "succeeded"} ('
            f'{len(rules)} rule{"" if len(rules) == 1 else "s"}, '
            f'{len(filepaths)} file{"" if len(filepaths) == 1 else "s"}, '
            f'{failures} violation{"" if failures == 1 else "s"}'
            f").",
            fg="bright_green" if failures == 0 else "bright_red",
        )
    )
    sys.exit(1 if failures != 0 else 0)
