# 🕷️ ReputePost Marketplace Scraper

A powerful, Python-based web scraper that automates login and data extraction from [reputepost.com](https://reputepost.com)'s buyer marketplace. This project uses **Scrapy**, **BeautifulSoup**, and **2Captcha** to **solve Cloudflare CAPTCHA (Turnstile)** and extract structured data into a CSV file.

---

## 🔍 Features

- ✅ Solves **Cloudflare Turnstile CAPTCHA** using [2Captcha](https://2captcha.com)
- ✅ Automated login using email, password, CSRF token, and CAPTCHA
- 🔁 Extracts listings across multiple paginated results
- 🌍 Scrapes key fields like:
  - Domain name
  - Prices (with multiple price types)
  - Country and language
  - Category
  - Link type and quantity
- 💾 Exports data to `Data.csv`
- 🧹 Automatically deletes old CSV files before new runs

---

## 🛠️ Requirements

- Python 3.8+
Create a `.env` file in the project root with the following keys:

```env
EMAIL=youremail@example.com
PASSWORD=yourpassword
API_KEY=your_2captcha_api_key
SITE_KEY=site_key_for_turnstile_captcha
```

## Dependencies (install with pip):
pip install -r requirements.txt

## ▶️ How to Use
1. Configure environment variables:
   Set up a .env file as described above.
2. Run the scraper:
   python run_spider.py
3. Result:
   Output saved to Data.csv

## 🧠 How It Works
1. Solves Cloudflare Turnstile CAPTCHA with the help of 2Captcha
2. Logs into ReputePost using dynamic CSRF tokens and session cookies
3. Submits paginated POST requests to scrape structured data
4. Parses HTML using BeautifulSoup
5. Outputs clean data into a CSV using Scrapy's feed exporter

## 🧪 Sample Output (CSV)
| domain      | marketplace    | price | secondPrice | currency | country | language | category | Info                       |
| ----------- | -------------- | ----- | ----------- | -------- | ------- | -------- | -------- | -------------------------- |
| example.com | reputepost.com | 80    | 50          | USD      | Canada  | English  | Finance  | Type of link: DoFollow\... |
