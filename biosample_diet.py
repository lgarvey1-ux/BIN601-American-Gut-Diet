"""BIN 601 Final Project — Liam Garvey

Read a list of American Gut BioSample IDs and save the diet type and IBS responses to a CSV.
Example: python biosample_diet.py examples/ComparisonAccessionList.txt
"""

import argparse
import csv
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def read_ids(path):
    """Read one numeric BioSample ID or SAM accession per line."""
    ids = []
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        value = line.strip()
        if not value:
            continue
        if not re.fullmatch(r"(?:\d+|SAM[NED][A-Z]?\d+)", value):
            raise ValueError(f"Invalid BioSample ID on line {number}: {value}")
        if value not in ids:
            ids.append(value)
    if not ids:
        raise ValueError("The input file contains no BioSample IDs.")
    return ids


def parse_survey(html):
    """Find the table with the diet type or IBS question."""
    page = BeautifulSoup(html, "html.parser")
    for table in page.find_all("table"):
        answers = {}
        for row in table.find_all("tr"):
            question = row.find("th")
            answer = row.find("td")
            if question is not None and answer is not None:
                key = question.get_text(" ", strip=True).lower().replace("_", " ")
                answers[key] = answer.get_text(" ", strip=True)
        if "diet type" in answers or "ibs" in answers:
            return answers
    return {}


def main():
    # Read the input filename and the optional CSV filename.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Text file with one BioSample ID per line")
    parser.add_argument("--output", type=Path, default=Path("diet_results.csv"))
    args = parser.parse_args()
    try:
        sample_ids = read_ids(args.input)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    # Write the CSV header before looking up the first ID.
    fields = ["BioSample_ID", "Question", "Answer", "IBS_Response", "Status"]
    completed = 0
    with args.output.open("w", newline="", encoding="utf-8-sig") as file, requests.Session() as session:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        file.flush()
        # Look up each BioSample ID and check the survey table for both answers.
        for position, sample_id in enumerate(sample_ids, 1):
            record = dict.fromkeys(fields, "")
            record.update(BioSample_ID=sample_id, Question="diet type")
            try:
                response = session.get(
                    "https://www.ncbi.nlm.nih.gov/biosample/",
                    params={"term": sample_id}, timeout=30,
                )
                response.raise_for_status()
                answers = parse_survey(response.text)
                record["Answer"] = answers.get("diet type", "")
                record["IBS_Response"] = answers.get("ibs", "")
                record["Status"] = "ok" if record["Answer"] else "diet response missing"
                if not answers:
                    record["Status"] = "survey table missing"
                if record["Answer"]:
                    completed += 1
            except requests.RequestException as error:
                record["Status"] = f"request failed: {error}"
            # Save the row now so the results are available while the script runs.
            writer.writerow(record)
            file.flush()
            print(f"{position}/{len(sample_ids)} {sample_id}: {record['Status']}")
            if position < len(sample_ids):
                time.sleep(1)
    print(f"Saved {completed} diet responses from {len(sample_ids)} unique IDs to {args.output.resolve()}")


if __name__ == "__main__":
    main()
