#!/usr/bin/env python3
"""
Test Verification Script for Adaptive Learning Platform

This script verifies that all test infrastructure is properly set up
and provides a summary of test coverage.
"""
import os
import sys
from pathlib import Path


def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists and report status."""
    exists = Path(filepath).exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {description}: {filepath}")
    return exists


def main():
    print("=" * 70)
    print("Test Infrastructure Verification")
    print("=" * 70)
    print()
    
    all_good = True
    
    # Backend Test Files
    print("Backend Test Infrastructure:")
    print("-" * 70)
    
    backend_files = [
        ("backend/pytest.ini", "Pytest configuration"),
        ("backend/conftest.py", "Test fixtures and configuration"),
        ("backend/run_tests.sh", "Test runner script"),
        ("backend/tests/__init__.py", "Tests package"),
        ("backend/tests/unit/__init__.py", "Unit tests package"),
        ("backend/tests/integration/__init__.py", "Integration tests package"),
        ("backend/tests/property/__init__.py", "Property tests package"),
    ]
    
    for filepath, desc in backend_files:
        if not check_file_exists(filepath, desc):
            all_good = False
    
    print()
    
    # Backend Test Files
    print("Backend Test Files:")
    print("-" * 70)
    
    test_files = [
        ("backend/tests/unit/test_agents.py", "Agent unit tests"),
        ("backend/tests/integration/test_api_endpoints.py", "API integration tests"),
        ("backend/tests/property/test_skill_assessment.py", "Property 1: Skill Assessment"),
        ("backend/tests/property/test_learning_path_progression.py", "Property 2: Path Progression"),
        ("backend/tests/property/test_resource_curation.py", "Property 3: Resource Curation"),
        ("backend/tests/property/test_schedule_optimization.py", "Property 4: Schedule Optimization"),
        ("backend/tests/property/test_reallocation.py", "Property 5: Reallocation"),
    ]
    
    for filepath, desc in test_files:
        if not check_file_exists(filepath, desc):
            all_good = False
    
    print()
    
    # Frontend Test Files
    print("Frontend Test Infrastructure:")
    print("-" * 70)
    
    frontend_files = [
        ("jest.config.js", "Jest configuration"),
        ("jest.setup.js", "Jest setup"),
        ("package.json", "Package configuration"),
        ("tests/property/skill-assessment.test.ts", "Frontend property tests"),
    ]
    
    for filepath, desc in frontend_files:
        if not check_file_exists(filepath, desc):
            all_good = False
    
    print()
    
    # Documentation
    print("Documentation:")
    print("-" * 70)
    
    doc_files = [
        ("TESTING_GUIDE.md", "Comprehensive testing guide"),
        ("TESTING_QUICKSTART.md", "Quick start guide"),
        ("PHASE_4_TESTING_SUMMARY.md", "Phase 4 summary"),
    ]
    
    for filepath, desc in doc_files:
        if not check_file_exists(filepath, desc):
            all_good = False
    
    print()
    print("=" * 70)
    
    if all_good:
        print("✓ All test infrastructure files are in place!")
        print()
        print("Next Steps:")
        print("  1. Install backend dependencies: cd backend && pip install -r requirements.txt")
        print("  2. Install frontend dependencies: npm install")
        print("  3. Run backend tests: cd backend && pytest")
        print("  4. Run frontend tests: npm test")
        print()
        print("For more information, see TESTING_QUICKSTART.md")
        return 0
    else:
        print("✗ Some test infrastructure files are missing!")
        print("Please review the output above and create missing files.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
