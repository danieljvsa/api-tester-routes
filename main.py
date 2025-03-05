import json
import argparse
import sys
from api_tester import APITester
import template

def main():
    parser = argparse.ArgumentParser(description="API Testing Tool")

    # Config file options
    parser.add_argument("--config", "-f", help="Path to JSON configuration file")
    parser.add_argument("--create-template", help="Create a template configuration file")
    parser.add_argument("--route", "-r", action="append", help="Specify route names to test (can be used multiple times)")

    # Single route options (for backward compatibility)
    parser.add_argument("--url", help="API endpoint URL")
    parser.add_argument("--method", "-m", default="GET", 
                        help="HTTP method (GET, POST, PUT, etc.)")
    parser.add_argument("--headers", "-H", help="HTTP headers in JSON format")
    parser.add_argument("--body", "-b", help="Request body in JSON format")
    parser.add_argument("--params", "-p", help="URL parameters in JSON format")
    parser.add_argument("--body-file", help="Path to JSON file containing request body")

    # Testing options
    parser.add_argument("--requests", "-n", type=int, default=10,
                        help="Number of requests for performance testing")
    parser.add_argument("--concurrent", "-c", action="store_true",
                        help="Send requests concurrently")
    parser.add_argument("--output", "-o", help="Save results to this file")
    parser.add_argument("--detail", "-d", action="store_true",
                        help="Show detailed response for a single request")

    # Add dependency installation helper
    parser.add_argument("--install-deps", action="store_true",
                        help="Install required dependencies")

    args = parser.parse_args()

    # Handle dependency installation
    if args.install_deps:
        print("Installing required dependencies...")
        import subprocess
        subprocess.call([sys.executable, "-m", "pip", "install", "requests", "tabulate", "lorem-text"])
        print("Dependencies installed successfully.")
        return

    # Handle template creation
    if args.create_template:
        template.save_config_template(args.create_template)
        return

    # Process config file if provided
    if args.config:
        try:
            config = template.load_config_file(args.config)
            template.run_tests_from_config(config, args)
            return
        except ValueError as e:
            print(f"Error: {str(e)}")
            return

    # Fallback to single route mode
    if args.url:
        # Parse JSON inputs
        headers = {}
        body = {}
        params = {}

        if args.headers:
            try:
                headers = json.loads(args.headers)
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in headers")
                return

        # Handle body from file or command line
        if args.body_file:
            try:
                with open(args.body_file, 'r') as f:
                    body = json.load(f)
            except Exception as e:
                print(f"Error loading body file: {str(e)}")
                return

        if args.body:
            try:
                if isinstance(args.body, str):
                    body_data = json.loads(args.body)
                else:
                    body_data = args.body
                body.update(body_data)
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in body")
                return

        if args.params:
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in params")
                return

        # Create tester for single route
        tester = APITester(args.url, args.method, headers, body, params)

        if args.detail:
            # Run a single request and show details
            tester.send_request()
            tester.print_response_details()
        else:
            # Run performance test
            results = tester.run_performance_test(args.requests, args.concurrent)
            tester.print_results(results)

            if args.output:
                tester.save_results(results, args.output)
    else:
        print("Error: Either a configuration file (--config) or URL (--url) is required.")
        print("Use --create-template to generate a sample configuration file.")
        print("Or use --install-deps to install required dependencies.")


if __name__ == "__main__":
    main()