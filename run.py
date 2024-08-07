from budget import Budget
from expense import Expense
import sys
import re
import os
import gspread
import time
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("pp3-holiday-budget-tracker")


def main():
    """
    Display a welcome message and directs to the Main Menu
    """
    welcome_message()

    main_menu()


def welcome_message():
    """
    Display welcome message to the user with prompt to confirm entry
    """
    clear_screen()
    ascii_art = r"""
                _ _ _ ____ _    ____ ____ _  _ ____    ___ ____
                | | | |___ |    |    |  | |\/| |___     |  |  |
                |_|_| |___ |___ |___ |__| |  | |___     |  |__|

                _  _ ____ _    _ ___  ____ _   _
                |__| |  | |    | |  \ |__|  \_/
                |  | |__| |___ | |__/ |  |   |

                ___  _  _ ___  ____ ____ ___
                |__] |  | |  \ | __ |___  |
                |__] |__| |__/ |__] |___  |

                ___ ____ ____ ____ _  _ ____ ____ |
                |  |__/ |__| |    |_/  |___ |__/  |
                |  |  \ |  | |___ | \_ |___ |  \  .

                """
    print(ascii_art)
    input("""
            Press 'Enter' to get started with creating a budget,
            adding an expense, or viewing a budget breakdown...
          """
          )
    clear_screen()


def main_menu():
    """
    Display Main Menu to the user with the core functions: create a new holiday
    budget, add an expense, see a budget breakdown, or exit the program
    """
    while True:
        clear_screen()
        print("What would you like to do?")
        print("  1. Create new holiday budget")
        print("  2. Add an expense")
        print("  3. See budget breakdown")
        print("  4. Exit program \n")

        choice = input("Enter number 1-4: \n").strip()
        if choice == "1":
            clear_screen()
            new_budget = create_new_budget()
            clear_screen()
            if new_budget:
                print(
                    f"You have entered {new_budget.amount:.2f} "
                    f"to be spent in {new_budget.name}...\n"
                )
                add_budget_sheet(new_budget)
                clear_screen(3)

        elif choice == "2":
            clear_screen()
            new_expense = get_expense()
            if new_expense:
                add_expense_to_budget(new_expense)
                print(new_expense)
                clear_screen(3)

        elif choice == "3":
            clear_screen()
            selected_budget = select_budget()
            if selected_budget:
                budget_breakdown(selected_budget)
                clear_screen(3)

        elif choice == "4":
            exit_program()

        else:
            input(f"Invalid input. Press 'Enter' to try again...\n")


def clear_screen(delay_sec=None):
    """
    Clears screen
    """
    if delay_sec is not None:
        time.sleep(delay_sec)
    os.system("clear")


def is_valid_amount(amount):
    """
    Checks is the number entered is a positive number
    with up to two decimal places
    """
    pattern = r"^\d+(\.\d{1,2})?$"
    return re.match(pattern, amount) is not None


def create_new_budget():
    """
    Create a new budget with new name and new total
    """
    clear_screen()
    budget_name = input("Enter your destination: \n").strip()

    while True:
        budget_amount_input = input("Enter total of budget: \n")

        if is_valid_amount(budget_amount_input):
            budget_amount = round(float(budget_amount_input), 2)
            new_budget = Budget(name=budget_name, amount=budget_amount)
            return new_budget

        else:
            print(
                f"Invalid input.  Please enter a positive number "
                f"with up to 2 decimal places.\n"
            )


def add_budget_sheet(budget):
    """
    Add a new worksheet to the existing spreadsheet with the budget details
    """
    print("Adding new budget...\n")
    # Ensure sheet name is unique
    sheet_name = budget.name
    existing_sheets = [sheet.title for sheet in SHEET.worksheets()]

    count = 2
    while sheet_name in existing_sheets:
        sheet_name = f"{budget.name} {count}"
        count += 1

    # Add new budget worksheet to spreadsheet
    new_sheet = SHEET.add_worksheet(title=sheet_name, rows=100, cols=20)

    # Populate new sheet with budget details
    new_sheet.update(range_name="A1:B1",
                     values=[["Destination:", budget.name]]
                     )
    new_sheet.update(range_name="A2:B2",
                     values=[["Budget Total:", budget.amount]]
                     )
    new_sheet.update(
                     range_name="A3:D3",
                     values=[["Category", "Expense Name", "Amount"]]
                     )
    print(
        f"New budget '{sheet_name}' created with "
        f"{budget.amount:.2f} to spend 💸\n"
    )


def get_expense():
    """
    Gets the details of the user's expense and adds it to the worksheet
    """
    clear_screen()
    worksheets = SHEET.worksheets()
    selected_budget = select_budget()
    if not selected_budget:
        return None
    clear_screen()
    expense_category = choose_expense_category()
    clear_screen()
    expense_name = input("Enter name of expense: \n")
    clear_screen()
    expense_amount = get_expense_amount()
    clear_screen()

    return Expense(
        category=expense_category,
        name=expense_name,
        amount=expense_amount,
        budget_name=selected_budget.title,
    )


def select_budget():
    """
    Create a menu for the user to choose which budget to work on
    """
    worksheets = SHEET.worksheets()

    # Check if there are any budget worksheets
    if len(worksheets) <= 1:
        clear_screen()
        print("No budgets found.  Please create a budget first.\n")
        input("Press 'Enter' to return to the main menu...")
        clear_screen()
        return None

    while True:
        print("Please select a budget from the list below:\n")
        for i, sheet in enumerate(worksheets):
            if i == 0:
                continue
            else:
                print(f"  {i}.{sheet.title}")

        budget_value_range = f"[1 - {len(worksheets) - 1}]"
        selected_budget_input = input(
            f"\nEnter a budget number {budget_value_range}: \n"
        )
        try:
            selected_budget_index = int(selected_budget_input)
            if selected_budget_index in range(1, len(worksheets)):
                selected_budget = worksheets[selected_budget_index]
                return selected_budget
                clear_screen()
            else:
                input(
                    f"Invalid budget selected. Press 'Enter' to try again...\n"
                     )
                clear_screen()

        except ValueError:
            input(f"Invalid input. Press 'Enter' to try again...\n")
            clear_screen()


def get_expense_amount():
    """
    Get amount of expense from the user
    """
    while True:
        expense_amount_input = input("Enter expense amount: \n")

        try:
            if is_valid_amount(expense_amount_input):
                expense_amount = round(float(expense_amount_input), 2)
                return expense_amount
                clear_screen()
            else:
                print(
                    "Invalid input.  Please enter a positive number "
                    f"with up to 2 decimal places.\n"
                )
                input(f"Press 'Enter' to try again.")
                clear_screen()

        except ValueError:
            print(
                "Invalid input.  Please enter a positive number "
                f"with up to 2 decimal places.\n"
            )
            input(f"Press 'Enter' to try agin.")
            clear_screen()


def choose_expense_category():
    """
    Display list of expense categories and let user choose which one to enter
    """
    expense_categories = [
        "Accommodation 🏨",
        "Travel ✈️",
        "Food 🍔",
        "Entertainment 🎉",
        "Miscellaneous 🛍️",
    ]

    while True:

        print("Select an expense category: ")
        for i, category_name in enumerate(expense_categories):
            print(f"  {i + 1}. {category_name}")

        value_range = f"[1 - {len(expense_categories)}]"
        selected_category_input = input(
                                        f"\nEnter a category number "
                                        f"{value_range}: \n")

        try:
            selected_category_index = int(selected_category_input) - 1
            if selected_category_index in range(len(expense_categories)):
                selected_category = expense_categories[selected_category_index]
                return selected_category
                clear_screen()
            else:
                input(
                      f"Invalid category selected. Press 'Enter' "
                      f"to try again...\n")
                clear_screen()

        except ValueError:
            input(f"Invalid input. Press 'Enter' to try again...")
            clear_screen()


def add_expense_to_budget(expense):
    """
    Update budget worksheet, add new row with the expense data provided
    """
    print("Updating budget file...\n")
    budget_worksheet = SHEET.worksheet(expense.budget_name)
    expense_data = [expense.category, expense.name, expense.amount]
    budget_worksheet.append_row(expense_data)
    print("Budget updated successfully!")


def sum_expenses(budget_worksheet):
    """
    Calculate how much the user has spent from a particular budget
    """
    expense_column = budget_worksheet.col_values(3)[3:]
    total_expenses = sum(
        float(expense) for expense in expense_column
        if is_valid_amount(expense)
    )
    return total_expenses


def calculate_remaining_budget(budget_name, budget_amount):
    """
    Calculate the remaining budget amount
    """
    budget_worksheet = SHEET.worksheet(budget_name)
    total_expenses = sum_expenses(budget_worksheet)
    remaining_budget = budget_amount - total_expenses
    return remaining_budget


def budget_breakdown(selected_budget):
    """
    Calculate and display how much the user
    has spent and how much they have left
    """
    clear_screen()
    print("Calculating budget...")
    total_expenses = sum_expenses(selected_budget)
    selected_budget_amount = float(selected_budget.col_values(2)[1])
    remaining_budget = calculate_remaining_budget(
        selected_budget.title, selected_budget_amount
    )
    clear_screen()
    print(f"Budget Breakdown:")
    print(
        f"You have spent {total_expenses:.2f} of {selected_budget_amount:.2f} "
        f"from your {selected_budget.title} budget."
    )
    print(f"You have {remaining_budget:.2f} left.\n")


def exit_program():
    """
    Lets the user either restart or exit the programme
    """
    clear_screen()
    print("Thank you for using Holiday Budget Tracker! Bon Voyage! ✈️\n")
    exit_input = input(
                        f"To restart program press Y, "
                        f"otherwise press any key to end program:  \n"
    )
    if exit_input.lower() == "y":
        welcome_message()
    else:
        sys.exit()


if __name__ == "__main__":
    main()
