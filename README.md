# CrowdWisdomTrading AI Agent - Internship Assessment

## Project Overview
This project implements a backend Python script using CrewAI to identify X (Twitter) creators who actively post about US financial markets. The script filters users based on specific criteria: more than 5000 followers and more than 5 tweets in the last 2 weeks.

## Technical Requirements
*   **Language**: Python 3.9+
*   **Framework**: CrewAI (latest version)
*   **LLM Provider**: LiteLLM (configured to use any compatible model, e.g., OpenAI GPT-4, Gemini-Pro)
*   **X (Twitter) Data Retrieval**: Tweepy (for detailed user information and recent tweets) and Snscrape (for initial tweet searching).

## Project Scope
The CrewAI workflow involves the following agents and tasks:
1.  **Keyword Generation Agent**: Generates relevant search keywords for US financial markets.
2.  **User Search Agent**: Uses the generated keywords to search X (Twitter) for tweets, extracts unique usernames, and then retrieves detailed user profiles (follower count, recent tweet activity) using the X (Twitter) API (via Tweepy). It then filters users based on the specified criteria.
3.  **Result Formatting Agent**: Formats the filtered user data into a JSON file, including overall statistics.

## Deliverables
*   Python script (`main.py`, `tools.py`, `requirements.txt`)
*   JSON output file (`financial_creators.json`)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd <your-repository-name>
```

### 2. Create and Activate a Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
Create a `.env` file in the project root directory and add your API keys:

```
# .env
OPENAI_API_KEY="YOUR_OPENAI_API_KEY" # Or your chosen LiteLLM model API key
TWITTER_BEARER_TOKEN="YOUR_TWITTER_BEARER_TOKEN_V2"
```
*   **LiteLLM**: Replace `YOUR_OPENAI_API_KEY` with the API key for your chosen LLM (e.g., OpenAI, Anthropic, Google). You can specify the model in `main.py` or as an environment variable `LITELLM_MODEL`.
*   **Twitter API v2**: You will need a Twitter Developer account to obtain a Bearer Token for the Twitter API v2. This is essential for retrieving detailed user information like follower counts and recent tweet activity.

## How to Run the Script

After setting up the environment and API keys, run the main script:

```bash
python main.py
```

## Expected Output
The script will generate a `financial_creators.json` file in the project root directory. The JSON file will contain a list of X (Twitter) users who meet the criteria, along with overall statistics such as processing time, total users found, and total users filtered.

Example `financial_creators.json` output structure:
```json
{
    "overall_statistics": {
        "processing_time": "X.XX seconds",
        "total_users_found": Y,
        "total_users_filtered": Z
    },
    "users": [
        {
            "url": "https://twitter.com/username1",
            "username": "username1",
            "followers": 12345,
            "avg_posts_per_week": 3.5
        },
        // ... more users
    ]
}
```

## Notes on Limitations (Snscrape)
While `snscrape` is used for initial tweet searching, it has limitations in reliably providing detailed user metrics like follower counts and precise recent tweet activity directly from tweet search results. The `search_x_users` tool with `tweepy` is designed to mitigate this by making direct API calls for user profiles, but it heavily relies on having a valid `TWITTER_BEARER_TOKEN`.

## Future Enhancements (Extra Credit Considerations)
*   **RAG with YouTube Videos**: Integrate CrewAI RAG to include information from YouTube videos related to financial markets into the agent's knowledge base, potentially enhancing keyword generation or user filtering.
*   **Logging and Error Handling**: Implement a more robust logging system (e.g., using Python's `logging` module) for better observability and error management.
*   **Multi-modal Processing**: Explore identifying and processing relevant images (e.g., charts, infographics) using multi-modal models to extract additional insights from X (Twitter) content.
