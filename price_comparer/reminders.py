"""Read (and optionally complete) items in an Apple Reminders list.

Uses JavaScript for Automation via ``osascript`` so it only runs on macOS.
The first run triggers a macOS privacy prompt: allow your terminal app to
control Reminders (System Settings > Privacy & Security > Automation).
iCloud-shared lists such as "Shopping - Family" work as long as they are
visible in the Reminders app on this Mac.
"""
from __future__ import annotations

import json
import platform
import subprocess
from pathlib import Path

from .models import ShoppingItem

DEFAULT_LIST = "Shopping - Family"

_READ_JXA = r"""
function run(argv) {
  const app = Application('Reminders');
  const matches = app.lists.whose({name: argv[0]})();
  if (matches.length === 0) { throw new Error('LIST_NOT_FOUND'); }
  const open = matches[0].reminders.whose({completed: false});
  const ids = open.id(), names = open.name(), bodies = open.body();
  return JSON.stringify(ids.map((id, i) => ({id: id, name: names[i], notes: bodies[i] || ''})));
}
"""

_COMPLETE_JXA = r"""
function run(argv) {
  const app = Application('Reminders');
  argv.forEach(id => { app.reminders.byId(id).completed = true; });
  return String(argv.length);
}
"""


class RemindersError(RuntimeError):
    pass


def _osascript(script: str, args: list[str]) -> str:
    if platform.system() != "Darwin":
        raise RemindersError(
            "Apple Reminders is only reachable from macOS. "
            "Run this on your Mac, or use --items-file for a plain-text list."
        )
    proc = subprocess.run(
        ["osascript", "-l", "JavaScript", "-e", script, *args],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        msg = proc.stderr.strip()
        if "LIST_NOT_FOUND" in msg:
            raise RemindersError(f"Reminders list not found: {args[0]!r}")
        if "-1743" in msg or "Not authorized" in msg:
            raise RemindersError(
                "macOS blocked access to Reminders. Allow your terminal under "
                "System Settings > Privacy & Security > Automation > Reminders."
            )
        raise RemindersError(msg or "osascript failed")
    return proc.stdout.strip()


def parse_reminders_json(payload: str) -> list[ShoppingItem]:
    items = []
    for row in json.loads(payload or "[]"):
        name = (row.get("name") or "").strip()
        if name:
            items.append(ShoppingItem(name=name, reminder_id=row.get("id"), notes=row.get("notes") or ""))
    return items


def load_from_reminders(list_name: str = DEFAULT_LIST) -> list[ShoppingItem]:
    return parse_reminders_json(_osascript(_READ_JXA, [list_name]))


def load_from_file(path: str | Path) -> list[ShoppingItem]:
    """Plain-text fallback: one item per line; ``item | zh: 中文`` adds notes."""
    items = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, _, notes = line.partition("|")
        items.append(ShoppingItem(name=name.strip(), notes=notes.strip().replace(";", "\n")))
    return items


def mark_completed(reminder_ids: list[str]) -> int:
    ids = [i for i in reminder_ids if i]
    if not ids:
        return 0
    return int(_osascript(_COMPLETE_JXA, ids) or 0)
