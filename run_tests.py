#!/usr/bin/env python3
"""
MT5 to MatchTrader MVP Test Runner
Runs all tests and provides a summary
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests and provide summary"""
    print("🧪 Running MT5 to MatchTrader MVP Test Suite...")
    print("=" * 60)
    
    # Add the project directory to Python path
    project_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_dir)
    
    # Run pytest with detailed output
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/",
        "-v",
        "--tb=short",
        "--disable-warnings",
        "--color=yes"
    ], cwd=project_dir)
    
    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("✅ All tests passed! Your MVP is production-ready! 🎉")
    else:
        print("❌ Some tests failed. Please check the output above.")
        print("💡 Tip: Most failures are due to missing implementations.")
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
