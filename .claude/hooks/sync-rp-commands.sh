#!/bin/bash
# Auto-create .claude/commands/rp-*.md symlink when docs/skills/rp-*.md is written.
# Hook input: JSON on stdin with tool_input.file_path.
# Fails open (exit 0) so harness workflow is never blocked by this helper.

set -u

file_path="$(jq -r '.tool_input.file_path // empty' 2>/dev/null)"
[ -z "${file_path:-}" ] && exit 0

base="$(basename "$file_path")"

case "$file_path" in
  */claude-projects/docs/skills/rp-*.md)
    project_root="$(git -C "$(dirname "$file_path")" rev-parse --show-toplevel 2>/dev/null)"
    [ -z "${project_root:-}" ] && exit 0
    target="$project_root/.claude/commands/$base"
    if [ ! -e "$target" ] && [ ! -L "$target" ]; then
      ( cd "$project_root/.claude/commands" && ln -s "../../docs/skills/$base" "$base" ) \
        && echo "[sync-rp-commands] symlink created: .claude/commands/$base" >&2
    fi
    ;;
esac

exit 0
