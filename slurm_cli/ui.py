from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .analyze import NEAR_MEM_LIMIT, NEAR_TIME_LIMIT
from .formatting import fmt_mb, fmt_time
from .models import Finding, JobRecord

STATE_STYLE = {
    "COMPLETED": "green",
    "RUNNING": "cyan",
    "PENDING": "cyan",
    "CANCELLED": "yellow",
}
LEVEL_STYLE = {
    "error": ("✖", "red"),
    "warn": ("▲", "yellow"),
    "info": ("•", "cyan"),
}
BAR_WIDTH = 20
MAX_WIDTH = 80


def _bar(ratio: float, warn_at: float) -> Text:
    filled = round(min(ratio, 1.0) * BAR_WIDTH)
    if ratio >= 1.0:
        style = "red"
    elif ratio >= warn_at:
        style = "yellow"
    else:
        style = "green"
    return Text.assemble(
        ("█" * filled, style),
        ("░" * (BAR_WIDTH - filled), "dim"),
        f"  {ratio:.0%}",
    )


def _usage_row(used: float, limit: float, fmt, warn_at: float) -> Text:
    return Text.assemble(_bar(used / limit, warn_at), f"   {fmt(used)} of {fmt(limit)}")


def show_job(job: JobRecord, findings: list[Finding], console: Console | None = None) -> None:
    console = console or Console()
    width = min(console.width, MAX_WIDTH)
    state_color = STATE_STYLE.get(job.state, "red")

    facts = Table.grid(padding=(0, 2))
    facts.add_column(style="dim", no_wrap=True)
    facts.add_column()

    state_text = Text(job.state, style=f"bold {state_color}")
    if job.exit_code or job.signal:
        state_text.append(f"   exit {job.exit_code}:{job.signal}", style="dim")
    facts.add_row("State", state_text)

    if job.timelimit_s:
        facts.add_row("Time", _usage_row(job.elapsed_s, job.timelimit_s, fmt_time, NEAR_TIME_LIMIT))
    else:
        facts.add_row("Time", fmt_time(job.elapsed_s))

    if job.max_rss_mb is not None and job.req_mem_mb:
        facts.add_row("Memory", _usage_row(job.max_rss_mb, job.req_mem_mb, fmt_mb, NEAR_MEM_LIMIT))
    else:
        facts.add_row("Memory", Text("not measured", style="dim"))

    facts.add_row("CPUs", str(job.alloc_cpus))
    facts.add_row("Node", job.node or "-")

    findings_grid = Table.grid(padding=(0, 1))
    findings_grid.add_column(no_wrap=True)
    findings_grid.add_column()
    for f in findings:
        icon, style = LEVEL_STYLE.get(f.level, ("•", "white"))
        findings_grid.add_row(Text(icon, style=style), Text(f.message))

    body = Group(facts, Text(""), findings_grid) if findings else facts
    title = Text.assemble((f"Job {job.job_id}", "bold"), f"  {job.name}")
    console.print(
        Panel(
            body,
            title=title,
            title_align="left",
            border_style=state_color,
            width=width,
            padding=(1, 2),
        )
    )
