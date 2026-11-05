# 0xlawyoor — Life OS

Seven Claude Code subagents running on the existing Notion Second Brain. No new databases.

```mermaid
flowchart TD
    U([Sebastian]) --> CoS[chief-of-staff<br/>routing · brief · WIP≤3]
    G[(Gmail · Drive)] --> IT[inbox-triage<br/>08:30 HKT sync]
    IT --> CC[(Command Centre Items)]
    CC --> CoS
    CoS --> GC[gc-counsel<br/>OSL · Job]
    CoS --> CA[career-agent<br/>Hustle · time-boxed]
    CoS --> BV[brand-voice<br/>talks · teaching]
    CoS --> FA[family-admin<br/>bills · ledger · family time]
    CoS --> WC[wellbeing-coach<br/>Sunday check-in]
    WC -. 3-line load signal only .-> CoS
    GC & CA & BV & FA --> D{{Drafts → your approval}}
    D --> Cal[(Google Calendar)]
    D --> CC
```

## Cadence
| When | Command | Agent |
|---|---|---|
| Weekdays ~08:13 HKT (scheduled) | `sync` then `morning brief` + approval table | inbox-triage → chief-of-staff |
| Two fixed weekly blocks | `career block` | career-agent |
| Sunday ~18:41 HKT (scheduled) | `weekly check-in` → `weekly review` | wellbeing-coach → chief-of-staff |
| Monthly | `ledger review` | family-admin |
| Quarterly | `refresh regulatory tracker` | brand-voice |

Rules: see `CLAUDE.md`.
