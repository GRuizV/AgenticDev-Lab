# Learning Log: Water Tracker CLI Tool

## Project Overview

This project involved creating a simple CLI tool to track daily water intake. The tool allows users to log the amount of water they drink and stores the data in a log file.

## Main Features

*   Logs water intake with timestamp.
*   Supports ml and cups as units of measurement.
*   Validates user input for amount and unit.
*   Interacts with the user via the command line.
*   Includes comments for better readability and understanding.

## Stages and Modifications

1.  **Initial Setup:**
    *   Created a basic Python script to log water intake with a timestamp.
    *   Used `argparse` to handle command-line arguments for water amount.
2.  **Unit of Measurement:**
    *   Modified the script to accept the unit of measurement (ml or cups).
    *   Added a conversion from cups to ml for consistent logging.
3.  **Error Handling:**
    *   Implemented error handling to ensure the amount is a positive number.
4.  **File Handling:**
    *   Added a check to create the log file if it doesn't exist.
5.  **Interactive CLI:**
    *   Modified the script to interact with the user via the command line.
    *   Removed `argparse` and used `input()` to get user input.
    *   Added a loop to allow multiple entries to be logged.
6.  **Code Documentation:**
    *   Added comments to the script to improve readability and understanding.

## Knowledge Gained

*   Using `argparse` for command-line arguments (initial stage).
*   Handling user input with `input()`.
*   Validating user input.
*   Working with timestamps and file I/O.
*   Structuring a CLI application for interactive use.
*   Documenting code with comments.

## Future Improvements

*   Add support for different log file formats (e.g., CSV, JSON).
*   Implement a feature to view daily/weekly/monthly summaries.
*   Allow users to set daily goals and track their progress.
*   Add a graphical user interface (GUI) for easier interaction.