#!/usr/bin/env python3
"""
Test runner script for yf_api.py

This script provides convenient commands for running different types of tests.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> bool:
    """Run a command and return whether it succeeded."""
    print(f"\n🧪 {description}")
    print(f"Command: {' '.join(command)}")
    print("-" * 50)

    try:
        subprocess.run(command, cwd=Path(__file__).parent, check=True)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (exit code: {e.returncode})")
        return False


def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py <command>")
        print("\nAvailable commands:")
        print("  all       - Run all tests")
        print("  unit      - Run only unit tests (fast)")
        print("  slow      - Run only integration tests (slow)")
        print("  coverage  - Run tests with coverage report")
        print("  watch     - Run tests in watch mode")
        sys.exit(1)

    command = sys.argv[1]
    base_cmd = ["uv", "run", "python", "-m", "pytest", "tests/"]

    success = True

    if command == "all":
        success = run_command(base_cmd + ["-v"], "Running all tests")

    elif command == "unit":
        success = run_command(
            base_cmd + ["-v", "-k", "not TestIntegration"], "Running unit tests only"
        )

    elif command == "slow":
        success = run_command(
            base_cmd + ["-v", "-m", "slow"], "Running integration tests only"
        )

    elif command == "coverage":
        # First check if coverage is available
        try:
            subprocess.run(
                ["uv", "run", "python", "-c", "import coverage"],
                check=True,
                capture_output=True,
            )
            success = run_command(
                base_cmd + ["--cov=yf_api", "--cov-report=term-missing", "-v"],
                "Running tests with coverage",
            )
        except subprocess.CalledProcessError:
            print("❌ Coverage not available. Install with: uv add coverage pytest-cov")
            success = False

    elif command == "watch":
        print("🔄 Running tests in watch mode (Ctrl+C to stop)")
        try:
            # Install pytest-watch if not available
            subprocess.run(["uv", "add", "pytest-watch"], check=False)
            subprocess.run(["uv", "run", "ptw", "tests/", "--", "-v"])
        except KeyboardInterrupt:
            print("\n⏹️  Watch mode stopped")
        except FileNotFoundError:
            print("❌ pytest-watch not available. Install with: uv add pytest-watch")
            success = False

    else:
        print(f"❌ Unknown command: {command}")
        success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
