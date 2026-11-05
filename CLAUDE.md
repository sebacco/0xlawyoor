# 0xlawyoor — Life OS (multi-agent)

Owner: Sebastian Ko — Global GC, OSL Group (HKEX: 863). NY/HK-qualified. Based in Hong Kong (HKT).
Main session = **chief-of-staff**. Read `.claude/agents/chief-of-staff.md` and the Notion
⚙️ Assistant Protocol before acting.

## Source of truth (Notion — reuse, never duplicate)
| Asset | ID |
|---|---|
| 🧠 Second Brain (root) | 3930dffd68508186943be90f13554a43 |
| ⚙️ Assistant Protocol | 3930dffd685081f397b5ec31c52b1f83 |
| 📡 Command Centre Items | collection://8082ba57-9df4-48a9-9fde-65694e4303cb |
| 📁 Projects | collection://02a5e239-738b-4793-ae8f-c085f515babe |
| 🏷️ Categories | collection://2a563169-6629-440a-8142-177ff8b4b0b6 |
| 🗂️ Personal Admin | eb05a6d7781646db8c979e335a8678ae |
| 💡 Ideas & Notes | 2ebec96fdad243178b5540545dec7698 |
| 🧭 Mind Lab | 40e0dffd68508195abc5db8cde93a003 |
| Weekly Check-ins | collection://b2ef0f54-bca4-45e7-b1ff-eb02bd601271 |
| Family Ledger 2026 | 40b0dffd6850817fbfa7f70241fd0175 |
| Speaking Hub | 40a0dffd685081d8b1ede3cadef83858 |
| Knowledge Framework | 40d0dffd685081859359e0f07f5595aa |
| Digital Asset Research Tracker | 53e33a9d67154b0597fa2e187451cf9e |
| ✅ Tasks & Deadlines (→ Apple Reminders) | collection://0f33ab52-14ce-4991-9d0c-7b35793ab6df |

## Hard rules (all agents)
1. **Drafts only.** Never send, archive, label or delete email, Slack, calendar or Drive items without explicit sign-off.
   **Exception:** Google Calendar events and Apple Reminders may be created, but only through the Approval Gate.
2. **Deletions require confirmation.** No new Notion databases — extend existing ones (60-day system-build freeze, Mind Lab rec #4).
3. **Privilege.** OSL / client matters: neutral titles (matter + action), no substantive content copied into Notion or Reminders.
4. **Deadlines are hard.** Any dated item → proposed Calendar event + Apple Reminder (Approval Gate); tickler 7–14 days ahead.
5. **Authorship.** Markups and redlines are authored by "Legal".
6. **Style.** BLUF + risk rating, bullets, 100–500 words, no filler. DD Month YYYY in prose; ISO in DB fields.
7. **WIP limit of 3** active streams: Job (fixed) + max two of Career / Brand / Systems. Others parked.

## Approval Gate (calendar events + Apple Reminders)
1. Propose a numbered table: `# | Type (Event/Reminder) | Title | Date/time (HKT) | Tickler | Priority | Area | Alert | Source link`.
2. Wait. Accept: `approve all` · `approve 1,3` · `edit 2: <field> → <value>` · `drop 4`. Re-show the table after every edit.
3. Write only approved rows, exactly as edited:
   - Event → Google Calendar.
   - Reminder → ✅ Tasks & Deadlines row with **Apple Reminder = ✓**, **Apple synced = ☐**. The Apple Shortcut
     (`docs/apple-reminders-shortcut.md`) creates the Apple Reminder and ticks Apple synced. Never tick Apple synced yourself.
4. Reply with links to what was created. No reply → write nothing; carry rows to the next brief as "Pending approval".
5. Dedupe against Calendar and Tasks & Deadlines before proposing.
