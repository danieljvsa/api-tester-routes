# 🚀 Comprehensive API Testing Tool

## Overview

This Python-based API testing tool provides a robust, flexible solution for testing and performance benchmarking of API endpoints. With features like dynamic content generation, multi-route testing, and comprehensive performance analysis, it simplifies the process of API validation and load testing.

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Key Features

- **Dynamic Content Generation**
  - Automatic generation of realistic test data
  - Support for various content types (text, emails, dates, UUIDs)
  - Flexible parameter customization

- **Multi-Route Testing**
  - Test multiple API endpoints in a single configuration
  - Global headers and base URL support
  - Targeted route testing

- **Performance Analysis**
  - Concurrent and sequential request testing
  - Detailed timing statistics
  - Status code distribution
  - Request duration metrics

- **Flexible Configuration**
  - JSON-based configuration files
  - Command-line argument support
  - URL parameter substitution

## 🛠 Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Install Dependencies
```bash
python main.py --install-deps
```

### Required Libraries
- requests
- tabulate
- lorem-text

## 📝 Usage Examples

### 1. Create Configuration Template
```bash
python main.py --create-template api_config.json
```

### 2. Run Tests for All Routes
```bash
python main.py --config api_config.json
```

### 3. Test Specific Routes
```bash
python main.py --config api_config.json --route "Get Users" --route "Create User"
```

### 4. Single Route Testing
```bash
python main.py --url https://api.example.com/users \
                     --method POST \
                     --body '{"name": "Test User"}' \
                     --requests 50 \
                     --concurrent
```

## 📋 Configuration File Structure

```json
{
  "baseUrl": "https://api.example.com",
  "globalHeaders": {
    "Authorization": "Bearer TOKEN"
  },
  "routes": [
    {
      "name": "Get Users",
      "url": "/users",
      "method": "GET",
      "params": {
        "page": "1"
      }
    },
    {
      "name": "Create User",
      "url": "/users",
      "method": "POST",
      "body": {
        "username": "$generate_text(min_words=1)",
        "email": "$generate_email()",
        "profile": {
          "fullName": "$generate_text(min_words=2)"
        }
      }
    }
  ]
}
```

## 🔍 Dynamic Content Generators

- `$generate_text(min_words=3, max_words=10)`: Random text
- `$generate_paragraph()`: Random paragraph
- `$generate_uuid()`: Random UUID
- `$generate_email()`: Random email
- `$generate_phone()`: Random phone number
- `$generate_date()`: Random date
- `$generate_number(min_val=0, max_val=100)`: Random number
- `$generate_boolean()`: Random boolean
- `$from_options(["option1", "option2"])`: Pick from options

## 📊 Performance Testing Options

- `--requests (-n)`: Number of requests to send (default: 10)
- `--concurrent (-c)`: Send requests concurrently
- `--output (-o)`: Save results to a JSON file
- `--detail (-d)`: Show detailed response for a single request

## 🔒 Security Considerations

- Always be cautious with sensitive API endpoints
- Use environment variables or secure vaults for tokens
- Avoid testing production systems without permission

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🚦 Disclaimer

This tool is for testing and development purposes. Always respect API usage policies and terms of service.

## 📧 Contact

Daniel Sá - danielviana18@gmail.com

Project Link: [https://github.com/danieljvsa/api-tester-routes](https://github.com/danieljvsa/api-tester-routes)
