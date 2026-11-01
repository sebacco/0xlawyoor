"""Interactive flow:

1. Load open items from Apple Reminders ("Shopping - Family").
2. YOU approve which items to price-check (nothing is searched before this).
3. YOU approve which sites to search.
4. Search, normalise to HKD, show comparison.
5. YOU pick which offers to add to cart; the tool never checks out.
6. Export XLSX report + local cart CSV; optionally tick off reminders.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from . import reminders
from .browser import DEFAULT_PROFILE, open_browser, page_for
from .models import CartResult, Comparison, ShoppingItem
from .pricing import FALLBACK_HKD_RATES, fetch_live_rates, to_hkd
from .report import append_cart_csv, export_xlsx, print_table
from .selection import parse_selection
from .sites import SITES, make_amazon


def ask_selection(console, prompt: str, count: int, default: str = "none") -> list[int]:
    from rich.prompt import Prompt

    while True:
        ans = Prompt.ask(f"{prompt} [dim](e.g. 1,3,5-7 · all · none)[/]", default=default)
        try:
            return parse_selection(ans, count)
        except ValueError as e:
            console.print(f"[red]{e}[/]")


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="price-comparer", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", default=reminders.DEFAULT_LIST, help="Reminders list name")
    ap.add_argument("--items-file", help="Plain-text list instead of Apple Reminders")
    ap.add_argument("--sites", default=",".join(SITES), help="Comma list: " + ",".join(SITES))
    ap.add_argument("--amazon-domain", default="amazon.com", help="amazon.com / amazon.co.jp / ...")
    ap.add_argument("--results", type=int, default=3, help="Results per site per item")
    ap.add_argument("--live-fx", action="store_true", help="Fetch live FX rates (open.er-api.com)")
    ap.add_argument("--profile", type=Path, default=DEFAULT_PROFILE, help="Browser profile dir")
    ap.add_argument("--chromium-path", help="Use a specific Chromium binary")
    ap.add_argument("--headless", action="store_true", help="Hide browser (login must already exist)")
    ap.add_argument("--out", type=Path, default=Path.home() / ".price-comparer",
                    help="Folder for reports and cart.csv")
    ap.add_argument("--login", action="store_true", help="Open each site to log in, then exit")
    return ap


def main(argv: list[str] | None = None) -> int:
    from rich.console import Console
    from rich.prompt import Confirm

    args = build_parser().parse_args(argv)
    console = Console()
    sites = dict(SITES)
    sites["amazon"] = make_amazon(args.amazon_domain)

    if args.login:
        with open_browser(args.profile, False, executable_path=args.chromium_path) as (p, ctx):
            for s in sites.values():
                page = page_for(p, ctx, s)
                page.goto(s.build_search_url("test"))
                console.print(f"[cyan]{s.label}[/]: {s.login_hint}")
            input("Log in in each tab, then press Enter to save the session... ")
        return 0

    # 1. Load list
    try:
        items: list[ShoppingItem] = (reminders.load_from_file(args.items_file) if args.items_file
                                     else reminders.load_from_reminders(args.list))
    except reminders.RemindersError as e:
        console.print(f"[red]{e}[/]")
        return 2
    if not items:
        console.print(f"No open items in '{args.list}'.")
        return 0

    # 2. Approval gate: items
    console.rule(f"[bold]{args.list}[/] — {len(items)} open items")
    for i, it in enumerate(items, 1):
        extra = f" [dim]({', '.join(f'{k}: {v}' for k, v in it.query_overrides.items())})[/]" if it.query_overrides else ""
        console.print(f"  {i:>2}. {it.name}{extra}")
    picked = [items[i] for i in ask_selection(console, "Which items should I price-check?", len(items))]
    if not picked:
        console.print("Nothing approved — no searches run.")
        return 0

    # 3. Approval gate: sites
    wanted = [k.strip() for k in args.sites.split(",") if k.strip() in sites]
    console.print("Sites: " + "  ".join(f"{i}. {sites[k].label}" for i, k in enumerate(wanted, 1)))
    site_keys = [wanted[i] for i in ask_selection(console, "Search which sites?", len(wanted), "all")]
    if not site_keys:
        return 0
    console.print(f"\nAbout to search [bold]{len(picked)}[/] item(s) on "
                  f"[bold]{', '.join(sites[k].label for k in site_keys)}[/].")
    if not Confirm.ask("Proceed?", default=True):
        return 0

    rates = dict(FALLBACK_HKD_RATES)
    if args.live_fx:
        try:
            rates.update(fetch_live_rates())
        except Exception as e:
            console.print(f"[yellow]Live FX unavailable ({e}); using fallback rates.[/]")

    comparisons = [Comparison(item=it) for it in picked]
    cart: list[CartResult] = []
    with open_browser(args.profile, args.headless, executable_path=args.chromium_path) as (p, ctx):
        pages = {k: page_for(p, ctx, sites[k]) for k in site_keys}

        # 4. Search
        with console.status("Searching...") as status:
            for comp in comparisons:
                for k in site_keys:
                    s = sites[k]
                    status.update(f"{s.label}: {comp.item.name}")
                    try:
                        offers = s.search(pages[k], comp.item, args.results)
                        for o in offers:
                            o.price_hkd = to_hkd(o.price, o.currency, rates)
                        comp.offers.extend(offers)
                        if not offers:
                            comp.errors[s.label] = "no results (logged in? captcha?)"
                    except Exception as e:
                        comp.errors[s.label] = f"{type(e).__name__}: {str(e)[:80]}"
        numbered = print_table(console, comparisons)
        console.print("[dim]Green = cheapest in HKD before shipping/fees. Check pack size & seller before buying.[/]")

        # 5. Approval gate: cart
        if numbered:
            for i in ask_selection(console, "Add which offers to cart?", len(numbered)):
                o = numbered[i]
                site = next(sites[k] for k in site_keys if sites[k].label == o.site)
                res = site.add_to_cart(pages[site.key], o)
                if res.status == "manual" and not args.headless:
                    input(f"  {o.site}: {res.detail} Finish in the browser, then press Enter... ")
                    res = CartResult(o, "manual", "completed by user in browser")
                cart.append(res)
                console.print(f"  [{'green' if res.status == 'added' else 'yellow'}]{res.status}[/] {o.site} · {o.title[:60]}")

    # 6. Outputs
    out = export_xlsx(args.out / "reports" / f"comparison-{datetime.now():%Y%m%d-%H%M}.xlsx",
                      comparisons, cart)
    if cart:
        append_cart_csv(args.out / "cart.csv", cart)
    console.print(f"Report: {out}")

    done_ids = sorted({c.item.reminder_id for c in comparisons
                       if c.item.reminder_id and any(r.offer.item == c.item.name for r in cart)})
    if done_ids and Confirm.ask(f"Tick off {len(done_ids)} carted item(s) in Reminders?", default=False):
        reminders.mark_completed(done_ids)
    return 0
