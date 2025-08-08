"""
Updated run script to use the new modular MLB report system.
This replaces the old monolithic approach with a cached, modular one.
"""
import sys
import traceback
from main import MLBReportGenerator


def main():
    """Run the MLB report generation."""
    try:
        print("=" * 60)
        print("MLB Report Generator - Modular Version")
        print("=" * 60)
        
        generator = MLBReportGenerator()
        
        # Check command line arguments for options
        if len(sys.argv) > 1 and sys.argv[1] == "--quick":
            print("Running quick update...")
            result = generator.run_quick_update()
        else:
            print("Running full report generation...")
            result = generator.generate_full_report()
        
        print("\n" + "=" * 60)
        print("Report generation completed successfully!")
        print("=" * 60)
        
        return result
        
    except Exception as e:
        print(f"\nError during report generation: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    main()