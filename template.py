import requests
import time
import json
import statistics
import argparse
import random
import string
import uuid
import datetime
import os
import sys
from typing import Dict, Any, List, Union, Optional, Callable
from tabulate import tabulate
from concurrent.futures import ThreadPoolExecutor
import lorem  # For generating text placeholders
import DynamicContentGenerator

def load_config_file(config_path: str) -> Dict[str, Any]:
  """
  Load API configuration from a JSON file.

  Supports both single route and multiple routes format.
  """
  try:
      with open(config_path, 'r') as f:
          config = json.load(f)

      # Check if it's a multi-route configuration
      if "routes" in config:
          return config

      # Single route configuration should have a URL
      if "url" not in config:
          raise ValueError("Config file must contain 'url' field or 'routes' array")

      return {"routes": [config]}  # Convert to multi-route format
  except json.JSONDecodeError:
      raise ValueError(f"Invalid JSON format in {config_path}")
  except Exception as e:
      raise ValueError(f"Error loading config file: {str(e)}")


def save_config_template(filename: str) -> None:
  """Save a template configuration file with multiple routes."""
  template = {
      "routes": [
          {
              "name": "Get User Profile",
              "url": "https://api.example.com/users/{id}",
              "method": "GET",
              "headers": {
                  "Authorization": "Bearer YOUR_TOKEN",
                  "X-Request-ID": "$generate_uuid()"
              },
              "params": {
                  "include": "profile,preferences"
              },
              "urlParams": {
                  "id": "123456"
              }
          },
          {
              "name": "Create User",
              "url": "https://api.example.com/users",
              "method": "POST",
              "headers": {
                  "Content-Type": "application/json",
                  "Authorization": "Bearer YOUR_TOKEN",
                  "X-Request-ID": "$generate_uuid()"
              },
              "body": {
                  "username": "$generate_text(min_words=1, max_words=2)",
                  "email": "$generate_email()",
                  "profile": {
                      "fullName": "$generate_text(min_words=2, max_words=3)",
                      "bio": "$generate_paragraph()",
                      "phone": "$generate_phone()",
                      "birthdate": "$generate_date()"
                  },
                  "preferences": {
                      "newsletter": "$generate_boolean()",
                      "theme": "$from_options([\"light\", \"dark\", \"system\"])"
                  }
              }
          },
          {
              "name": "Update User",
              "url": "https://api.example.com/users/{id}",
              "method": "PUT",
              "headers": {
                  "Content-Type": "application/json",
                  "Authorization": "Bearer YOUR_TOKEN"
              },
              "urlParams": {
                  "id": "$generate_uuid()"
              },
              "body": {
                  "profile": {
                      "fullName": "$generate_text(min_words=2, max_words=3)",
                      "bio": "$generate_paragraph()"
                  }
              }
          }
      ],
      "globalHeaders": {
          "User-Agent": "API-Tester/1.0"
      },
      "baseUrl": "https://api.example.com"  # Optional base URL for all routes
  }

  with open(filename, 'w') as f:
      json.dump(template, f, indent=2)

  print(f"Template configuration saved to {filename}")
  print("\nDynamic Content Generation:")
  print("  $generate_text(min_words=3, max_words=10) - Generate random text")
  print("  $generate_paragraph() - Generate a paragraph")
  print("  $generate_uuid() - Generate a UUID")
  print("  $generate_email() - Generate an email address")
  print("  $generate_phone() - Generate a phone number")
  print("  $generate_date() - Generate a random date")
  print("  $generate_number(min_val=0, max_val=100) - Generate a random number")
  print("  $generate_boolean() - Generate a random boolean")
  print("  $from_options([\"option1\", \"option2\"]) - Pick from provided options")


def run_tests_from_config(config: Dict[str, Any], args) -> None:
  """Run tests for all routes in the configuration file."""
  routes = config.get("routes", [])
  base_url = config.get("baseUrl", "")
  global_headers = config.get("globalHeaders", {})

  if not routes:
      print("No routes defined in configuration file")
      return

  results = []

  # Process each route
  for i, route in enumerate(routes):
      # Check if we should run only specific routes
      if args.route and route.get("name") not in args.route:
          continue

      print(f"\n[{i+1}/{len(routes)}] Testing route: {route.get('name', 'Unnamed')}")

      # Combine URL (base + route)
      url = route["url"]
      if base_url and not url.startswith("http"):
          url = base_url.rstrip("/") + "/" + url.lstrip("/")

      # Apply URL parameters if any
      if "urlParams" in route:
          for param_name, param_value in route["urlParams"].items():
              url = url.replace(f"{{{param_name}}}", str(param_value))

      # Merge headers (global + route)
      headers = {**global_headers, **route.get("headers", {})}

      # Create tester
      tester = APITester(
          url=url,
          method=route.get("method", "GET"),
          headers=headers,
          body=route.get("body", {}),
          params=route.get("params", {})
      )

      if args.detail:
          # Run a single request and show details
          tester.send_request()
          tester.print_response_details()
      else:
          # Run performance test
          result = tester.run_performance_test(args.requests, args.concurrent)
          result["name"] = route.get("name", f"Route {i+1}")
          tester.print_results(result)
          results.append(result)

  # Save combined results if requested
  if args.output and results:
      combined_results = {
          "timestamp": datetime.datetime.now().isoformat(),
          "total_routes_tested": len(results),
          "routes": results
      }

      with open(args.output, 'w') as f:
          json.dump(combined_results, f, indent=2)
      print(f"\nCombined results saved to {args.output}")
