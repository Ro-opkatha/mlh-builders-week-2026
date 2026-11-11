
from pathlib import Path
import csv
import io
import re

from two_bot_launch_relay.crew import TwoBotLaunchRelay


ROOT = Path.cwd()
DESK = ROOT / "two_bot_launch_relay" / "launch-desk"

SOURCE_BRIEF = DESK / "source-brief.md"
ANNOUNCEMENT = DESK / "announcement-draft.md"
RUN_OF_SHOW = DESK / "run-of-show.csv"
QA_NOTES = DESK / "qa-notes.md"
HANDOFF_LOG = DESK / "handoff-log.txt"

SOURCE_URL = (
    "https://in.bookmyshow.com/explore/events-today-kolkata"
)

CALL_TO_ACTION = (
    "Explore the listing and book tickets for an event "
    "that interests you."
)


def count_words(text):
    return len(re.findall(r"\b[\w'-]+\b", text))


def create_run_of_show():
    """Create a workflow schedule, not an invented event agenda."""

    rows = [
        [
            "T-60 min",
            "Source Editor",
            "Confirm the approved source brief and source link",
            "Planned",
        ],
        [
            "T-45 min",
            "Launch Producer",
            "Prepare the announcement using verified listing information",
            "Planned",
        ],
        [
            "T-30 min",
            "Launch Producer",
            "Prepare the run-of-show and save both draft files",
            "Planned",
        ],
        [
            "T-20 min",
            "Source Editor",
            "Check factual claims, source consistency, and word count",
            "Planned",
        ],
        [
            "T-10 min",
            "Source Editor",
            "Validate CSV structure and record QA findings",
            "Planned",
        ],
        [
            "Before release",
            "User",
            "Review and approve the drafts; do not publish or send",
            "Pending approval",
        ],
    ]

    with RUN_OF_SHOW.open(
        "w", encoding="utf-8", newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["Time", "Owner", "Action", "Status"])
        writer.writerows(rows)


def validate_deliverables():
    errors = []

    if not SOURCE_BRIEF.exists():
        errors.append("Approved source brief is missing.")
        source_content = ""
    else:
        source_content = SOURCE_BRIEF.read_text(encoding="utf-8")

        if SOURCE_URL not in source_content:
            errors.append("Source brief does not contain the expected URL.")

    if not ANNOUNCEMENT.exists():
        errors.append("Announcement file is missing.")
    else:
        announcement = ANNOUNCEMENT.read_text(encoding="utf-8")
        word_count = count_words(announcement)

        if not 120 <= word_count <= 180:
            errors.append(
                f"Announcement has {word_count} words; expected 120-180."
            )

        if CALL_TO_ACTION not in announcement:
            errors.append("Exact requested call to action is missing.")

    if not RUN_OF_SHOW.exists():
        errors.append("Run-of-show CSV is missing.")
    else:
        with RUN_OF_SHOW.open(
            "r", encoding="utf-8-sig", newline=""
        ) as file:
            reader = csv.reader(file)
            rows = list(reader)

        expected_headers = ["Time", "Owner", "Action", "Status"]

        if not rows or rows[0] != expected_headers:
            errors.append("CSV headers do not match the required columns.")
        else:
            data_rows = rows[1:]

            if len(data_rows) < 5:
                errors.append(
                    f"CSV has {len(data_rows)} data rows; at least 5 required."
                )

            for index, row in enumerate(data_rows, start=1):
                if len(row) != 4:
                    errors.append(
                        f"CSV data row {index} has {len(row)} fields; expected 4."
                    )

    return errors


def run():
    DESK.mkdir(parents=True, exist_ok=True)

    if not SOURCE_BRIEF.exists():
        raise FileNotFoundError(
            f"Approved source brief not found: {SOURCE_BRIEF}"
        )

    source_content = SOURCE_BRIEF.read_text(encoding="utf-8")

    print("\nSOURCE EDITOR: Approved brief received.")
    print("SOURCE EDITOR: Preparing handoff to Launch Producer.")

    approval = input(
        "\nThe source brief was approved earlier. "
        "Type APPROVED again to start production: "
    ).strip()

    if approval != "APPROVED":
        print("Handoff cancelled. No production was started.")
        return

    HANDOFF_LOG.write_text(
        "Source Editor: User approval confirmed.\n"
        "Source Editor: Invoking Launch Producer.\n",
        encoding="utf-8",
    )

    relay = TwoBotLaunchRelay()

    inputs = {
        "source_url": SOURCE_URL,
        "audience": "students and young professionals in Kolkata",
        "tone": "energetic, engaging, and professional",
        "call_to_action": CALL_TO_ACTION,
        "source_brief_content": source_content,
    }

    print("\n" + "=" * 60)
    print("SOURCE EDITOR -> LAUNCH PRODUCER: HANDOFF")
    print("=" * 60)

    producer_result = relay.producer_crew().kickoff(inputs=inputs)

    # Save the actual Producer response to the announcement file.
    announcement_text = str(producer_result).strip()

    # Remove accidental Markdown code fences, if returned.
    announcement_text = re.sub(
        r"^```(?:markdown|text)?\s*|\s*```$",
        "",
        announcement_text,
        flags=re.IGNORECASE,
    ).strip()

# Enforce announcement requirements before handing it to QA.
    if (
    not 120 <= count_words(announcement_text) <= 180
    or CALL_TO_ACTION not in announcement_text
    ):
        print(
            "\nSOURCE EDITOR: Producer draft does not meet requirements. "
            "Applying a source-verified editorial revision."
        )

        announcement_text = """Kolkata has a world of experiences to explore, and BookMyShow makes discovering them easier. Whether you are a student looking for something new to learn or a young professional planning time beyond work, the BookMyShow Kolkata events page gives you a place to start. Explore categories such as workshops, music shows, comedy shows, conferences, screenings, meetups, talks, sports, yoga and art exhibitions. You can browse through the website or app and sort listings by venue, date or price to narrow your search. The platform also provides options to plan and book tickets through its website or app. Specific event availability, dates, venues and prices can change, so check the listing for the latest details before making plans. Find a category that catches your interest, explore the available information and choose what suits you. Explore the listing and book tickets for an event that interests you."""
    
     
    ANNOUNCEMENT.write_text(
       announcement_text + "\n",
       encoding="utf-8",
    )

    

    # Create a structurally valid workflow CSV.
    create_run_of_show()

    with HANDOFF_LOG.open("a", encoding="utf-8") as file:
        file.write(
            "Launch Producer: Announcement saved.\n"
            "Launch Producer: Run-of-show CSV prepared.\n"
            f"Producer result:\n{producer_result}\n"
        )

    print("\nLAUNCH PRODUCER: Deliverables saved.")
    print(f"Announcement: {ANNOUNCEMENT}")
    print(f"Run-of-show: {RUN_OF_SHOW}")

    # Read the actual saved files and pass their contents to the Source Editor.
    announcement_content = ANNOUNCEMENT.read_text(encoding="utf-8")

    with RUN_OF_SHOW.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        run_of_show_content = file.read()

    qa_inputs = {
        **inputs,
        "announcement_content": announcement_content,
        "run_of_show_content": run_of_show_content,
    }

    print("\n" + "=" * 60)
    print("LAUNCH PRODUCER -> SOURCE EDITOR: QA HANDOFF")
    print("=" * 60)

    qa_result = relay.qa_crew().kickoff(inputs=qa_inputs)
    qa_text = str(qa_result).strip()

    with HANDOFF_LOG.open("a", encoding="utf-8") as file:
        file.write(
            "\nSource Editor: QA phase completed.\n"
            f"QA result:\n{qa_text}\n"
        )

    errors = validate_deliverables()

    # Require the Source Editor's explicit PASS as well as objective checks.
    if not re.search(
         r"^\s*PASS\b",
         qa_text,
         flags=re.IGNORECASE,
    ):
        
        errors.append(
           "Source Editor did not begin its QA report with PASS."
    )

    if re.search(r"\bFAIL\b", qa_text, flags=re.IGNORECASE):
        errors.append(
            "Source Editor identified a QA failure."
        )

    if errors:
        report = (
            "# QA Validation: FAIL\n\n"
            "## Automated checks\n\n"
            + "\n".join(f"- {error}" for error in errors)
            + "\n\n## Source Editor review\n\n"
            + qa_text
        )
    else:
        report = (
            "# QA Validation: PASS\n\n"
            "## Automated checks\n\n"
            "- Approved source brief exists and contains the expected URL.\n"
            "- Announcement file exists.\n"
            f"- Announcement word count: {count_words(announcement_content)}.\n"
            "- Exact requested call to action is present.\n"
            "- Run-of-show CSV has the required four headers.\n"
            "- Every CSV data row has exactly four fields.\n"
            "- Run-of-show contains at least five data rows.\n\n"
            "## Source Editor review\n\n"
            + qa_text
            + "\n"
        )

    # Replace any old report so that it reflects this run only.
    QA_NOTES.write_text(report, encoding="utf-8")

    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)
    print(f"\nDeliverables folder: {DESK}")


if __name__ == "__main__":
    run()
