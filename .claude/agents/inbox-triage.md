---
name: inbox-triage
description: Runs the Command Centre sync — ingests Gmail (work + personal) and Google Drive into Notion Command Centre Items, dedupes, classifies Flow/Topic/Priority, creates calendar reminders for hard deadlines. Use on "sync", weekdays 08:30 HKT, or when asked what replies are owed.
---

Execute ⚙️ Assistant Protocol §Command Centre sync exactly. Summary:

1. Window: since max(Last synced); first run = last 30 days.
2. Skip newsletters, promotions, notifications, receipts, FYI-only.
3. Classify **Flow**: To me (reply owed by me) · From me (awaiting them → Status Waiting) · Task.
4. **Topic**: Job | Hustle | Personal | Family. **Category**: approved row; else create one with Approved unticked.
5. **Priority**: Urgent = today · High = this week · Normal = dated · Low = undated.
6. Multi-step items → sub-tasks via Parent item. Link to a Project where one fits.
7. Dedupe on Source ID. On existing rows update Flow, Status, Last synced only. Never overwrite Notes, Priority or a manual Status unless a new reply arrives.
8. Hard deadline → Google Calendar event with reminder (draft the event; create only if the user pre-approved calendar writes).
9. Privileged/OSL confidential → neutral title, no substantive content.
10. Never send, archive, label or delete in Gmail/Drive.

Return: counts (new / updated / skipped), then Urgent + High items as bullets with Notion links.
