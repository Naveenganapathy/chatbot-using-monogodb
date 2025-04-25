volunteer-connect-chatbot/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
└── utils.py (optional, for extra helper functions if needed)
# Volunteer Connect Chatbot 🤖

A smart chatbot to help users find volunteer opportunities by querying a MongoDB database and generating friendly responses using TinyLlama (Ollama).

## 🔥 Features
- MongoDB-backed event search
- Fuzzy matching on queries (e.g., "food donation Chennai")
- AI-generated friendly answers using TinyLlama model
- Easy to use via Streamlit web app

## 🛠️ Setup Instructions

1. Clone this repo.
2. Create a `.env` file based on `.env.example` with your MongoDB URI and Ollama URL.
3. Install dependencies:

```bash
pip install -r requirements.txt

---

# ✅ How it will work:

- User types a query ("food donation event Chennai").
- Streamlit searches MongoDB using **fuzzy matching**.
- Matches are shown in raw JSON.
- A detailed answer is generated via **TinyLlama** using the match data.
- Response is friendly and human-like.

---

# 🎯 Next Steps for you:

1. Create all these files.
2. Push them to GitHub.
3. Deploy on [Streamlit Cloud](https://streamlit.io/cloud).
4. Set your environment variables (MongoDB URI + Ollama URL) in Streamlit Cloud settings.

---
  
Would you also like me to give you a simple **GitHub push command guide** to do it fast? 🚀  
(If yes, I can send it step-by-step for your easy deployment.)
