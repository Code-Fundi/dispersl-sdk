#!/usr/bin/env python
"""
Comprehensive test runner for Dispersl Python SDK.
Supports different test categories and deployment configurations.
"""
import subprocess
import sys
import os
import argparse
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return the result."""
    if description:
        print(f"\n🔧 {description}")
        print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Dispersl Python SDK Test Runner")
    parser.add_argument(
        "test_type",
        choices=[
            "unit", "integration", "e2e", "all", "deploy", "deploy-ci",
            "client", "http", "auth", "serializers", "agentic", "retry",
            "workflows", "api", "complete"
        ],
        help="Type of tests to run"
    )
    parser.add_argument("--watch", "-w", action="store_true", help="Run in watch mode")
    parser.add_argument("--coverage", "-c", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--ci", action="store_true", help="CI mode (no interactive features)")
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = [sys.executable, "-m", "pytest"]
    
    # Add common options
    if args.verbose:
        base_cmd.append("-v")
    else:
        base_cmd.append("-q")
    
    if args.coverage:
        base_cmd.extend(["--cov=src/dispersl", "--cov-report=term-missing"])
    
    if args.watch and not args.ci:
        base_cmd.append("--watch")
    
    if args.ci:
        base_cmd.extend(["--ci", "--watchAll=false"])
    
    # Set environment variables for integration tests
    if args.test_type in ["integration", "e2e", "all", "deploy", "deploy-ci", "workflows", "api", "complete"]:
        os.environ["RUN_INTEGRATION_TESTS"] = "true"
        os.environ["DISPERSL_API_URL"] = os.environ.get("DISPERSL_API_URL", "http://localhost:3001/v1")
        os.environ["DISPERSL_API_KEY"] = os.environ.get("DISPERSL_API_KEY", "test_api_key")
    
    # Test type specific commands
    test_commands = {
        "unit": base_cmd + ["tests/unit/", "-m", "unit"],
        "integration": base_cmd + ["tests/integration/", "-m", "integration"],
        "e2e": base_cmd + ["tests/e2e/", "-m", "e2e"],
        "all": base_cmd + ["tests/", "-m", "unit or integration or e2e"],
        "deploy": base_cmd + ["tests/integration/", "tests/e2e/", "-m", "integration or e2e"],
        "deploy-ci": base_cmd + ["tests/integration/", "tests/e2e/", "-m", "integration or e2e", "--ci", "--coverage", "--cov-report=xml"],
        
        # Individual test files
        "client": base_cmd + ["tests/unit/test_client.py"],
        "http": base_cmd + ["tests/unit/test_http.py"],
        "auth": base_cmd + ["tests/unit/test_auth.py"],
        "serializers": base_cmd + ["tests/unit/test_serializers.py"],
        "agentic": base_cmd + ["tests/unit/test_agentic.py"],
        "retry": base_cmd + ["tests/unit/test_retry.py"],
        "workflows": base_cmd + ["tests/integration/test_workflow_integration.py"],
        "api": base_cmd + ["tests/integration/test_api_integration.py"],
        "complete": base_cmd + ["tests/e2e/test_complete_workflows.py"],
    }
    
    cmd = test_commands.get(args.test_type, base_cmd + ["tests/"])
    
    # Run the tests
    success = run_command(cmd, f"Running {args.test_type} tests")
    
    if success:
        print(f"\n✅ {args.test_type.title()} tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {args.test_type.title()} tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()