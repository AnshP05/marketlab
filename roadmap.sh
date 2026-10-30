#!/bin/sh
# Local read-only helper; unrelated to the roadmap.sh website.
set -eu

usage() {
    cat <<'USAGE'
Usage: ./roadmap.sh [status|next|list|help]
  status  Current milestone, active ticket, blockers, and learning status (default)
  next    One selected ticket and its acceptance criteria
  list    Milestone and queued-ticket overview
  help    Show this help
Reads docs/ROADMAP.md; never changes tasks, sources repo text, or uses the network.
This is a local shell script, not the roadmap.sh website.
USAGE
}

if [ "$#" -gt 1 ]; then
    usage >&2
    exit 2
fi

section=${1:-status}
case "$section" in
    help|-h|--help) usage; exit 0 ;;
    status|next|list) ;;
    *) printf 'Unknown command: %s\n' "$section" >&2; usage >&2; exit 2 ;;
esac

script_dir=$(CDPATH= cd -P "$(dirname "$0")" && pwd)
roadmap_file=$script_dir/docs/ROADMAP.md
if [ ! -r "$roadmap_file" ]; then
    printf 'Cannot read %s. Restore the local learning documents; see AGENTS.md.\n' "$roadmap_file" >&2
    exit 1
fi

# Only print bounded sections of Markdown. No eval/source or second state file.
awk -v section="$section" '
    $0 == "<!-- roadmap:" section ":start -->" { inside = 1; starts++; next }
    $0 == "<!-- roadmap:" section ":end -->" { inside = 0; ends++; next }
    inside { print }
    END { if (starts != 1 || ends != 1 || inside) exit 1 }
' "$roadmap_file"
