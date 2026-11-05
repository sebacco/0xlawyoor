# Apple Reminders bridge (Notion → Shortcuts → Reminders)

Apple has no cloud API for Reminders, so agents can't write to it directly. They write **approved** reminders
to ✅ Tasks & Deadlines with `Apple Reminder = ✓`. A Shortcut on your iPhone or Mac picks those rows up,
creates the reminders, and ticks `Apple synced`.

```mermaid
flowchart LR
    A[Agent proposes] --> B{You approve / edit}
    B -- approved --> C[(Notion ✅ Tasks & Deadlines<br/>Apple Reminder ✓ · Apple synced ☐)]
    C --> D[Shortcut: Life OS → Reminders<br/>runs 08:45 + 19:00 HKT]
    D --> E[Apple Reminders list "Life OS"]
    D --> F[Notion: Apple synced ✓]
```

## One-time setup (≈10 min)

### 1. Notion token
1. notion.so/profile/integrations → **New integration** → name `Life OS Shortcut`, type Internal → copy the secret.
2. Open ✅ Tasks & Deadlines → `•••` → **Connections** → add `Life OS Shortcut`.

### 2. Reminders list
Create a list called **Life OS** in Apple Reminders.

### 3. Build the Shortcut (Shortcuts app → +, name it `Life OS → Reminders`)
| # | Action | Setting |
|---|---|---|
| 1 | Text | your Notion secret (keep the Shortcut private) |
| 2 | Get Contents of URL | `https://api.notion.com/v1/databases/6fd81fe8da834da6af281e6255c92499/query` · Method **POST** · Headers: `Authorization: Bearer [Text]`, `Notion-Version: 2022-06-28`, `Content-Type: application/json` · Body JSON (below) |
| 3 | Get Dictionary Value | `results` |
| 4 | Repeat with Each | item in results |
| 5 | ↳ Get Dictionary Value | `properties.Task.title.1.plain_text` → *Title* |
| 6 | ↳ Get Dictionary Value | `properties.Due date.date.start` → *Due* |
| 7 | ↳ Get Dictionary Value | `url` → *Link* |
| 8 | ↳ Add New Reminder | Title = *Title*, List = **Life OS**, Alert = *Due* (date), Notes = *Link*, URL = *Link* |
| 9 | ↳ Get Contents of URL | `https://api.notion.com/v1/pages/[id]` · Method **PATCH** · same headers · Body `{"properties":{"Apple synced":{"checkbox":true}}}` |
| 10 | End Repeat | |

Body for step 2:
```json
{"filter":{"and":[
  {"property":"Apple Reminder","checkbox":{"equals":true}},
  {"property":"Apple synced","checkbox":{"equals":false}},
  {"property":"Status","select":{"does_not_equal":"Done"}}
]}}
```

### 4. Automate
Shortcuts → **Automation** → Time of Day → 08:45 and 19:00 daily → Run `Life OS → Reminders` → **Run Immediately** (off = asks first).

## Rules
- Only approved rows are ever flagged — the Approval Gate stays in front of this.
- Privileged/OSL items: titles are already neutral; no substantive content goes into Reminders.
- Ticking a reminder done in Apple does **not** write back to Notion (v1). Mark Done in Notion, or tell the chief-of-staff "done #ID".
