"""Data playground for exploring the Navitia API and train operators.

This module provides an interactive console interface to explore:
- Journey structures
- Operator analysis
- Eurostar train detection
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import all script functions
from src.api_explo.scripts.api_analysis import run_operator_analysis
from src.api_explo.scripts.check_eurostar import print_eurostar_check
from src.api_explo.scripts.inspect_journey_structure import (
    inspect_journey_structure,
    print_journey_structure,
)

load_dotenv()
API_KEY = os.getenv("SNCF_API_KEY")


def print_menu() -> None:
    """Print the main menu."""
    print("\n" + "=" * 80)
    print("TGV TIMES API PLAYGROUND")
    print("=" * 80)
    print("\nAvailable operations:")
    print("  1. Inspect journey structure")
    print("  2. Analyze operators at a station")
    print("  3. Check for Eurostar trains")
    print("  4. Run all analyses")
    print("  q. Quit")
    print()


def run_all_analyses() -> None:
    """Run all available analyses."""
    print("\n" + "=" * 80)
    print("RUNNING ALL ANALYSES")
    print("=" * 80)

    # 1. Journey structure
    print("\n\n1. JOURNEY STRUCTURE INSPECTION")
    print("-" * 80)
    journey = inspect_journey_structure()
    if journey:
        print_journey_structure(journey)

    # 2. Operator analysis
    print("\n\n2. OPERATOR ANALYSIS")
    print("-" * 80)
    run_operator_analysis(save_to_file=True)

    # 3. Eurostar check
    print("\n\n3. EUROSTAR CHECK")
    print("-" * 80)
    print_eurostar_check()


def main() -> None:
    """Main entry point for data playground."""
    if not API_KEY:
        print("ERROR: SNCF_API_KEY not found in environment")
        print("Please set it in your .env file")
        return

    while True:
        print_menu()
        choice = input("Select an operation (1-4, q): ").strip().lower()

        if choice == "q":
            print("\nExiting API playground. Goodbye!")
            break
        elif choice == "1":
            print("\n" + "=" * 80)
            print("JOURNEY STRUCTURE INSPECTION")
            print("=" * 80)
            journey = inspect_journey_structure()
            if journey:
                print_journey_structure(journey)
        elif choice == "2":
            print("\n" + "=" * 80)
            print("OPERATOR ANALYSIS")
            print("=" * 80)
            run_operator_analysis()
        elif choice == "3":
            print("\n" + "=" * 80)
            print("EUROSTAR CHECK")
            print("=" * 80)
            print_eurostar_check()
        elif choice == "4":
            run_all_analyses()
        else:
            print("Invalid choice. Please select 1-4 or q.")

        if choice in ["1", "2", "3", "4"]:
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
