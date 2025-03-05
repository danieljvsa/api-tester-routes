import requests
import time
import json
import statistics
from typing import Dict, Any
from tabulate import tabulate
from concurrent.futures import ThreadPoolExecutor
from dynamic_content_generator import DynamicContentGenerator

class APITester:
  def __init__(self, url: str, method: str = "GET", headers: Dict = None, 
               body: Dict = None, params: Dict = None):
      """
      Initialize API tester with request details.

      Args:
          url: The API endpoint URL
          method: HTTP method (GET, POST, PUT, DELETE, etc.)
          headers: HTTP headers to include in the request
          body: Request body for POST/PUT requests
          params: URL parameters for the request
      """
      self.url = url
      self.method = method.upper()
      self.headers = headers or {}
      self.body = body or {}
      self.params = params or {}
      self.response = None
      self.duration = 0
      self.content_generator = DynamicContentGenerator()

  def process_dynamic_content(self, data):
      """
      Process data structure recursively, replacing dynamic content markers.

      Looks for special syntax like "$generate_text()" or "$generate_uuid()" and
      replaces them with dynamically generated content.
      """
      if isinstance(data, dict):
          for key, value in list(data.items()):
              data[key] = self.process_dynamic_content(value)
          return data
      elif isinstance(data, list):
          return [self.process_dynamic_content(item) for item in data]
      elif isinstance(data, str) and data.startswith("$generate_"):
          # Extract function name and parameters
          try:
              func_str = data[1:]  # Remove the $
              func_name = func_str.split("(")[0]
              # Extract parameters if any
              params_str = func_str[len(func_name)+1:-1]  # Remove function name and parentheses

              # Parse parameters
              params = {}
              if params_str:
                  # Handle multiple parameters separated by commas
                  param_pairs = params_str.split(",")
                  for pair in param_pairs:
                      if "=" in pair:
                          k, v = pair.split("=", 1)
                          k = k.strip()
                          v = v.strip()
                          # Convert parameter value to appropriate type
                          if v.lower() == "true":
                              v = True
                          elif v.lower() == "false":
                              v = False
                          elif v.isdigit():
                              v = int(v)
                          elif v.startswith('"') and v.endswith('"'):
                              v = v[1:-1]  # Remove quotes
                          params[k] = v

              # Get the generator method
              generator_method = getattr(self.content_generator, func_name, None)
              if generator_method and callable(generator_method):
                  return generator_method(**params)
              else:
                  return f"Unknown generator: {func_name}"
          except Exception as e:
              return f"Error generating content: {str(e)}"
      else:
          return data

  def prepare_request_data(self):
      """Process all request data for dynamic content before sending."""
      self.headers = self.process_dynamic_content(self.headers)
      self.body = self.process_dynamic_content(self.body)
      self.params = self.process_dynamic_content(self.params)

  def send_request(self) -> requests.Response:
      """Send a single request and measure response time."""
      # Process dynamic content
      self.prepare_request_data()

      start_time = time.time()

      try:
          self.response = requests.request(
              method=self.method,
              url=self.url,
              headers=self.headers,
              json=self.body if self.method in ["POST", "PUT", "PATCH"] else None,
              params=self.params,
              timeout=30
          )
          self.duration = time.time() - start_time
          return self.response
      except Exception as e:
          print(f"Error: {str(e)}")
          self.duration = time.time() - start_time
          return None

  def run_performance_test(self, num_requests: int = 10, 
                           concurrent: bool = False) -> Dict[str, Any]:
      """
      Run multiple requests and collect performance statistics.

      Args:
          num_requests: Number of requests to send
          concurrent: Whether to send requests concurrently

      Returns:
          Dictionary with performance statistics
      """
      durations = []
      status_codes = []

      if concurrent:
          with ThreadPoolExecutor(max_workers=min(num_requests, 10)) as executor:
              for _ in range(num_requests):
                  # Create a new tester with the same configuration (for dynamic content)
                  tester = APITester(self.url, self.method, 
                                    self.headers.copy(), 
                                    self.body.copy(), 
                                    self.params.copy())
                  future = executor.submit(tester.send_request)
                  response = future.result()
                  if response:
                      durations.append(tester.duration)
                      status_codes.append(response.status_code)
      else:
          for _ in range(num_requests):
              # Create a new tester with the same configuration (for new dynamic content per request)
              tester = APITester(self.url, self.method, 
                                self.headers.copy(), 
                                self.body.copy(), 
                                self.params.copy())
              response = tester.send_request()
              if response:
                  durations.append(tester.duration)
                  status_codes.append(response.status_code)

      if not durations:
          return {"error": "All requests failed"}

      return {
          "url": self.url,
          "method": self.method,
          "requests_sent": num_requests,
          "successful_requests": len(durations),
          "min_time": min(durations),
          "max_time": max(durations),
          "avg_time": statistics.mean(durations),
          "median_time": statistics.median(durations),
          "status_codes": dict((code, status_codes.count(code)) 
                              for code in set(status_codes))
      }

  def print_results(self, results: Dict[str, Any]) -> None:
      """Pretty print test results."""
      if "error" in results:
          print(f"Error: {results['error']}")
          return

      print("\n=== API Test Results ===")
      print(f"URL: {results['url']}")
      print(f"Method: {results['method']}")
      print(f"Requests sent: {results['requests_sent']}")
      print(f"Successful requests: {results['successful_requests']}")

      # Format timing data
      print("\n--- Timing (seconds) ---")
      timing_table = [
          ["Minimum", f"{results['min_time']:.4f}s"],
          ["Maximum", f"{results['max_time']:.4f}s"],
          ["Average", f"{results['avg_time']:.4f}s"],
          ["Median", f"{results['median_time']:.4f}s"]
      ]
      print(tabulate(timing_table, tablefmt="simple"))

      # Status code distribution
      print("\n--- Status Codes ---")
      status_table = [[code, count] for code, count in results['status_codes'].items()]
      print(tabulate(status_table, headers=["Status Code", "Count"], tablefmt="simple"))

  def save_results(self, results: Dict[str, Any], filename: str) -> None:
      """Save test results to a JSON file."""
      with open(filename, 'w') as f:
          json.dump(results, f, indent=2)
      print(f"\nResults saved to {filename}")

  def print_response_details(self) -> None:
      """Print details about the most recent response."""
      if not self.response:
          print("No response available")
          return

      print("\n=== Response Details ===")
      print(f"Status Code: {self.response.status_code}")
      print(f"Response Time: {self.duration:.4f}s")

      print("\n--- Headers ---")
      for key, value in self.response.headers.items():
          print(f"{key}: {value}")

      print("\n--- Response Body ---")
      try:
          print(json.dumps(self.response.json(), indent=2))
      except:
          print(self.response.text)
