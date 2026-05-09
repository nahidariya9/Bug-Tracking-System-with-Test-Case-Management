
import json
import os

def generate():
    json_path = "coverage.json"

    if not os.path.exists(json_path):
        print("coverage.json not found. Run pytest first.")
        return

    with open(json_path) as f:
        data = json.load(f)

    lines = []
    lines.append("=" * 55)
    lines.append("COVERAGE REPORT — Per Module")
    lines.append("=" * 55)

    files = data.get("files", {})
    total_covered   = 0
    total_stmts     = 0

    for filepath, info in sorted(files.items()):
        # Clean up the path to just show app/routes/bugs.py style
        clean = filepath.replace("\\", "/")
        if "app/" in clean:
            clean = "app/" + clean.split("app/")[-1]

        summary      = info.get("summary", {})
        covered      = summary.get("covered_lines", 0)
        stmts        = summary.get("num_statements", 0)
        pct          = summary.get("percent_covered", 0.0)
        missing      = info.get("missing_lines", [])

        total_covered += covered
        total_stmts   += stmts

        missing_str = (
            ", ".join(str(l) for l in missing[:5])
            + ("..." if len(missing) > 5 else "")
        ) if missing else "None"

        lines.append(f"\nModule : {clean}")
        lines.append(f"  Statements : {stmts}")
        lines.append(f"  Covered    : {covered}")
        lines.append(f"  Coverage   : {pct:.1f}%")
        lines.append(f"  Missing    : {missing_str}")

    # Overall total
    overall = (total_covered / total_stmts * 100) if total_stmts > 0 else 0.0
    lines.append("\n" + "=" * 55)
    lines.append(f"TOTAL COVERAGE: {overall:.1f}%")
    lines.append("=" * 55)

    report = "\n".join(lines)
    with open("coverage_report.txt", "w") as f:
        f.write(report)

    print(report)
    print("\n✅ Saved to coverage_report.txt")

if __name__ == "__main__":
    generate()