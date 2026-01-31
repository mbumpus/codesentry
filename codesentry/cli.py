"""CLI interface for CodeSentry"""

import sys
from pathlib import Path

import click

from . import __version__
from .analyzer import AnalysisEngine
from .patterns import ALL_PATTERNS
from .reporter import Reporter


@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, help='Show version info')
@click.pass_context
def main(ctx, version):
    """CodeSentry - AI-Powered Code Analysis & Developer Education
    
    Scan Python files for anti-patterns and learn how to fix them.
    
    \b
    Examples:
      codesentry scan myfile.py
      codesentry scan myfile.py --teach
      codesentry scan myfile.py --quick
      codesentry patterns
    """
    if version:
        click.echo(f"CodeSentry v{__version__}")
        ctx.exit(0)
    elif ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.argument('file', type=click.Path(exists=True, path_type=Path))
@click.option('--teach', '-t', is_flag=True, help='Verbose mode with full explanations')
@click.option('--quick', '-q', is_flag=True, help='Minimal output - just issue type and line')
@click.option('--format', '-f', 'output_format', type=click.Choice(['text', 'json']), 
              default='text', help='Output format')
@click.option('--no-color', is_flag=True, help='Disable colored output')
def scan(file: Path, teach: bool, quick: bool, output_format: str, no_color: bool):
    """Scan a Python file for anti-patterns.
    
    \b
    Examples:
      codesentry scan app.py
      codesentry scan app.py --teach    # Full educational output
      codesentry scan app.py --quick    # Minimal lint-style output
      codesentry scan app.py -f json    # JSON output
    """
    # Validate file is Python
    if file.suffix != '.py':
        click.echo(f"Warning: {file} doesn't have .py extension", err=True)
    
    # Determine output mode
    if teach and quick:
        click.echo("Error: --teach and --quick are mutually exclusive", err=True)
        sys.exit(1)
    
    mode = 'teach' if teach else 'quick' if quick else 'default'
    
    # Run analysis
    engine = AnalysisEngine(ALL_PATTERNS)
    result = engine.analyze_file(file)
    
    # Report results
    reporter = Reporter(
        format=output_format,
        mode=mode,
        color=not no_color
    )
    reporter.report(result)
    
    # Exit with appropriate code
    # 0=clean, 1=warnings, 2=errors, 3=critical
    if result.parse_error:
        sys.exit(1)
    sys.exit(result.max_severity_code)


@main.command()
def version():
    """Show version information."""
    click.echo(f"CodeSentry v{__version__}")
    click.echo("AI-Powered Pattern-Aware Code Analysis & Developer Education Engine")
    click.echo("")
    click.echo(f"Patterns: {len(ALL_PATTERNS)} available")
    click.echo("Python: 3.9+")


@main.command()
@click.option('--verbose', '-v', is_flag=True, help='Show full pattern details')
def patterns(verbose: bool):
    """List all detectable patterns.
    
    Shows all anti-patterns that CodeSentry can detect, along with their
    severity levels and categories.
    """
    click.echo("")
    click.echo(click.style("CodeSentry Patterns", bold=True))
    click.echo("=" * 50)
    click.echo("")
    
    for p in ALL_PATTERNS:
        severity_colors = {
            'WARNING': 'yellow',
            'ERROR': 'red', 
            'CRITICAL': 'red',
        }
        severity_name = p.severity.name
        severity_styled = click.style(severity_name.lower(), fg=severity_colors.get(severity_name, 'white'))
        
        click.echo(click.style(f"{p.id}: {p.name}", bold=True))
        click.echo(f"  Category: {p.category}")
        click.echo(f"  Severity: {severity_styled}")
        click.echo(f"  {p.description}")
        
        if verbose:
            teaching = p.get_teaching()
            click.echo("")
            click.echo(click.style("  Why it matters:", fg='cyan'))
            click.echo(f"    {teaching.why[:100]}...")
        
        click.echo("")


if __name__ == "__main__":
    main()
