from __future__ import annotations
from email.message import EmailMessage
import smtplib

def maybe_alert(skill_counts: dict[str, int], target_skill: str, min_mentions: int,
                sender: str | None, recipient: str | None, app_password: str | None):
    if not sender or not recipient or not app_password:
        return
    mentions = skill_counts.get(target_skill.lower(), 0)
    if mentions < min_mentions:
        return

    msg = EmailMessage()
    msg["Subject"] = f"[Job Trends] Spike detected: {target_skill} ({mentions} mentions)"
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(f"""Heads up!

Skill: {target_skill}
Mentions today: {mentions}

— Job Skills Demand Monitor
""")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)
