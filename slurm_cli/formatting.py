def fmt_time(seconds: float) -> str:
    s = int(round(seconds))
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"

# Format like Slurm --mem syntacx (G / M)
def fmt_mb(mb: float) -> str:
    if mb >= 1024:
        return f"{mb / 1024:.1f}G"
    if mb >= 10:
        return f"{mb:.0f}M"
    return f"{mb:.1f}M"
