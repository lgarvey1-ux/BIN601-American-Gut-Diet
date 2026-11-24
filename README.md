# BIN 601 Final Project

Liam Garvey

## What this project asks

What diet types did the American Gut records in my IBS and non-IBS groups report?

I used the survey lookup from my BIN 501 R Shiny app as the starting point for this script. Give it a list of BioSample IDs and it saves the diet type and reported IBS response for each ID in a CSV.

## 1. Set up and run the script

Open Anaconda Prompt in the project folder. Install the packages once:

```bat
python -m pip install -r requirements.txt
```

Run the script with the combined list:

```bat
python biosample_diet.py examples/ComparisonAccessionList.txt --output comparison_diet.csv
```

Use one numeric NCBI BioSample ID or SAM accession per line. You can use any length list with at least one ID. The script skips blank lines and repeated IDs. If a line has an invalid ID, Python shows the line number before making any requests. Run the command from the project folder or use full paths for the input and output. The BioSample lookup needs an internet connection. Running the command again replaces the CSV at the output path.

## 2. Choose an example list

| File | Records |
| --- | --- |
| `examples/ComparisonAccessionList.txt` | All 97 IDs |
| `examples/IBSAccessionList.txt` | 49 records reporting medically diagnosed IBS |
| `examples/NonIBSAccessionList.txt` | 48 records reporting no IBS |

## 3. Check the output

Open `comparison_diet.csv` and check the `BioSample_ID`, `Question`, `Answer`, `IBS_Response`, and `Status` columns. The question in this export is `diet type`. The diet and IBS answers use the wording from the BioSample page. If the diet answer is blank, check `Status` to see whether the request failed, the survey table was missing, or the table had no diet response.

The included CSV has 97 rows with both responses filled in and all statuses marked `ok`. A live spot check reran three IDs and matched the saved rows. The two group lists were checked against the combined list.

These are the records I selected for the Shiny project. I chose the groups separately, so the results describe these records. Some people may have more than one sample. I only used the survey responses here. The CSV does not measure microbiome diversity or show whether diet causes IBS.

## How the script works

1. `read_ids` reads the list, checks the IDs, and keeps the first copy of each ID.
2. `main` requests a BioSample page for each ID. It gives each request up to 30 seconds and waits one second between records.
3. `parse_survey` reads the table with the diet type or IBS question. It treats underscores and spaces the same way when checking the question names.
4. The CSV writer saves each row as soon as the script finishes checking that ID.

## Sources

- [NCBI BioSample](https://www.ncbi.nlm.nih.gov/biosample/)
- [My BIN 501 Shiny app](https://liamgarvey.shinyapps.io/bin501-diet-types-ibs/)
