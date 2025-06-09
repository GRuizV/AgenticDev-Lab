import datetime  # Import the datetime module for handling timestamps
import os  # Import the os module for file system operations

def log_water_intake(amount, unit):
    """
    Logs the water intake amount to a file with a timestamp.
    Args:
        amount (float): The amount of water consumed.
        unit (str): The unit of measurement (ml or cups).
    """
    # Validate the amount
    if amount <= 0:
        print("Please enter a positive amount.")
        return

    # Validate the unit
    if unit not in ['ml', 'cups']:
        print("Invalid unit. Please use 'ml' or 'cups'.")
        return

    # Get the current timestamp
    timestamp = datetime.datetime.now().isoformat()

    # Convert cups to ml if necessary
    if unit == 'cups':
        amount_ml = amount * 240  # Approximate conversion
        log_string = f"{timestamp}: {amount} cups ({amount_ml} ml)\n"
    else:
        amount_ml = amount
        log_string = f"{timestamp}: {amount} ml\n"
    
    # Create the log file if it doesn't exist
    if not os.path.exists("water_log.txt"):
        open("water_log.txt", "w").close()

    # Write the log entry to the file
    with open("water_log.txt", "a") as log_file:
        log_file.write(log_string)
    
    # Print a confirmation message
    print(f"Logged {amount} {unit} at {timestamp}")

def main():
    """
    Main function to handle user interaction and log water intake.
    """
    while True:
        try:
            # Get the amount of water from the user
            amount = float(input("Enter the amount of water you drank (or 'q' to quit): "))
            # Get the unit of measurement from the user
            unit = input("Enter the unit of measurement (ml or cups): ").lower()
            # Log the water intake
            log_water_intake(amount, unit)
        except ValueError:
            print("Invalid input. Please enter a number for the amount.")
        except Exception as e:
            print(f"An error occurred: {e}")

        # Ask the user if they want to log another entry
        choice = input("Do you want to log another entry? (y/n): ").lower()
        if choice != 'y':
            break

if __name__ == "__main__":
    # Call the main function if the script is executed
    main()