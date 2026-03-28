🚀 LinkedIn AI Leads Scraper

An intelligent LinkedIn lead generation tool that automates profile discovery and extracts high-quality leads using network-based exploration and smart filtering.

Designed for founders, marketers, and developers to scale outreach and eliminate manual prospecting.

✨ Features
🔍 Automated Lead Discovery – Find relevant LinkedIn profiles starting from seed users
🌐 Network-Based Exploration – Discover similar profiles recursively (tree-based scraping)
⚡ Fast & Scalable Scraping – Parallel processing for efficient data extraction
♻️ Smart Deduplication – Automatically removes duplicate leads
📊 Structured Data Export – Export leads in CSV / JSON format
📈 Real-Time Progress Tracking – Monitor leads as they are discovered

This tool can scale from a few profiles to thousands of leads in minutes by leveraging LinkedIn’s network recommendations.

🛠️ Tech Stack
Language: Python
Automation / Scraping: API-based / custom scraping logic
Data Handling: Pandas / JSON
Config: .ini based configuration
📦 Installation
git clone https://github.com/Trillionaretanker/linkdin-ai-leads.git
cd linkdin-ai-leads
pip install -r requirements.txt
⚙️ Configuration
Open the config.ini file
Add your API key / credentials:
[LINKEDIN_API]
api_key = YOUR_API_KEY
▶️ Usage
python main.py
Steps:
Choose how you want to start:
From usernames
From file input
Enter seed LinkedIn profiles
Select discovery depth
Let the scraper automatically generate leads
📁 Output

The scraper generates structured lead data like:

{
  "name": "John Doe",
  "headline": "Software Engineer",
  "company": "Google",
  "location": "India",
  "profile_url": "https://linkedin.com/in/johndoe"
}
🧠 How It Works
Starts from initial LinkedIn profiles
Uses “People Also Viewed” / network signals to find similar users
Expands recursively (tree-based discovery)
Filters duplicates and structures data

This approach allows exponential lead discovery compared to manual search.

⚠️ Disclaimer

This project is for educational purposes only.
Scraping LinkedIn may violate their Terms of Service.

Use responsibly and at your own risk.

🤝 Contributing

Contributions are welcome!

Fork the repo
Create a new branch
Make your changes
Submit a pull request
📬 Contact

Manasvi Rajendra

💼 LinkedIn: https://linkedin.com/in/your-profile
💻 GitHub: https://github.com/Trillionaretanker
