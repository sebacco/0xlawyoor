"""Comparison table (terminal) and XLSX/CSV export."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from .models import CartResult, Comparison, Offer

NAVY, CYAN, MINT, SLATE = "0B1F3A", "00C2FF", "3DFFB8", "2E3A4D"


def flat_offers(comparisons: list[Comparison]) -> list[Offer]:
    return [o for c in comparisons for o in c.offers]


def print_table(console, comparisons: list[Comparison]) -> list[Offer]:
    """Render numbered offers grouped by item; returns them in display order."""
    from rich.table import Table

    numbered: list[Offer] = []
    for comp in comparisons:
        best = comp.best()
        t = Table(title=f"[bold]{comp.item.name}[/]", title_justify="left", header_style="bold cyan")
        for col, kw in (("#", {"justify": "right"}), ("Site", {}), ("Product", {"max_width": 60}),
                        ("Price", {"justify": "right"}), ("HKD", {"justify": "right"})):
            t.add_column(col, **kw)
        ordered = sorted(comp.offers, key=lambda o: (o.price_hkd is None, o.price_hkd or 0))
        for o in ordered:
            numbered.append(o)
            hkd = f"{o.price_hkd:,.2f}" if o.price_hkd is not None else "–"
            style = "bold green" if o is best else ""
            price = f"{o.currency} {o.price:,.2f}" if o.price is not None else o.raw_price or "–"
            t.add_row(str(len(numbered)), o.site, o.title, price, hkd, style=style)
        for site, err in comp.errors.items():
            t.add_row("", site, f"[red]{err}[/]", "", "")
        console.print(t)
    return numbered


def export_xlsx(path: Path, comparisons: list[Comparison], cart: list[CartResult]) -> Path:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    wb = Workbook()
    ws = wb.active
    ws.title = "Comparison"
    head_fill, head_font = PatternFill("solid", fgColor=NAVY), Font(bold=True, color="FFFFFF")
    best_fill = PatternFill("solid", fgColor=MINT)

    ws.append([f"Price comparison — {datetime.now():%Y-%m-%d %H:%M}"])
    ws["A1"].font = Font(bold=True, size=14, color=NAVY)
    ws.append([])
    headers = ["Item", "Site", "Product", "Price", "Currency", "Price (HKD)", "Best", "URL"]
    ws.append(headers)
    for c in ws[3]:
        c.fill, c.font = head_fill, head_font
    for comp in comparisons:
        best = comp.best()
        for o in sorted(comp.offers, key=lambda o: (o.price_hkd is None, o.price_hkd or 0)):
            ws.append([comp.item.name, o.site, o.title, o.price, o.currency, o.price_hkd,
                       "✓" if o is best else "", o.url])
            if o is best:
                for c in ws[ws.max_row][:7]:
                    c.fill = best_fill
    for col, width in zip("ABCDEFGH", (24, 18, 60, 10, 9, 12, 6, 50)):
        ws.column_dimensions[col].width = width
    ws.freeze_panes = "A4"

    cs = wb.create_sheet("Cart")
    cs.append(["Item", "Site", "Product", "Price (HKD)", "Status", "Detail", "URL"])
    for c in cs[1]:
        c.fill, c.font = PatternFill("solid", fgColor=SLATE), head_font
    for r in cart:
        o = r.offer
        cs.append([o.item, o.site, o.title, o.price_hkd, r.status, r.detail, o.url])
    total = sum(r.offer.price_hkd or 0 for r in cart)
    cs.append([])
    cs.append(["", "", "Total (HKD, ex-shipping)", round(total, 2)])
    cs.cell(cs.max_row, 3).font = Font(bold=True, color=CYAN)
    for col, width in zip("ABCDEFG", (24, 18, 60, 12, 10, 40, 50)):
        cs.column_dimensions[col].width = width
    for row in ws.iter_rows(min_row=4):
        row[2].alignment = Alignment(wrap_text=True, vertical="top")

    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return path


def append_cart_csv(path: Path, cart: list[CartResult]) -> None:
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp", "item", "site", "title", "price_hkd", "status", "url"])
        for r in cart:
            o = r.offer
            w.writerow([datetime.now().isoformat(timespec="seconds"), o.item, o.site, o.title,
                        o.price_hkd, r.status, o.url])
