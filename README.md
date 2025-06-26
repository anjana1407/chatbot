Context-Based AI Chatbot

A simple Streamlit app that answers questions strictly based on user-provided training content. It also supports generating short professional emails from context-based queries.

Features

* Accepts and stores custom training content
* Answers only from the provided content using Mixtral-8x7B (Together AI)
* Responds with a fixed message if content is missing or unrelated
* Optional email generation based on queries
* Clean chat interface with session history

Setup

1. Install dependencies

    pip install -r requirements.txt

3. Add your Together API key
4. 
   * Set it as an environment variable: `TOGETHER_API_KEY`
   * Or add to `.streamlit/secrets.toml`:


     TOGETHER_API_KEY = "your_api_key_here"
 

5. Run the app
   
   streamlit run main.py
   
