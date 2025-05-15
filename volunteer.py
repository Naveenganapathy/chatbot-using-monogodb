from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
from pymongo import MongoClient
import streamlit as st
from dotenv import load_dotenv
import os
import re
from datetime import datetime
from difflib import get_close_matches

# Load environment variables
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

# MongoDB setup
client = MongoClient(mongo_uri)
db = client["volunteer"]
collection = db["volunteer_roles"]

# Streamlit UI
st.title("🤖 Volunteer Connect Show Chat Bot")

locations = collection.distinct("location")
months = list(range(1, 13))
selected_location = st.selectbox("📍 Filter by Location (optional):", ["All"] + sorted(locations))
selected_month = st.selectbox("📅 Filter by Month (optional):", ["All"] + months)
input_txt = st.text_input("💬 Please enter your query...")

# Month name mapping
MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12
}

def extract_month(query):
    for month, num in MONTH_MAP.items():
        if month in query.lower():
            return num
    return None

def extract_keywords(query):
    stopwords = {"in", "on", "for", "with", "near", "at", "is", "the", "a", "an", "me", "i", "to", "event"}
    words = re.findall(r'\w+', query.lower())
    return [word for word in words if word not in stopwords]

def fuzzy_match(field_value, keyword):
    return keyword in field_value.lower() or get_close_matches(keyword, [field_value.lower()], n=1, cutoff=0.85)

def search_roles(query):
    keywords = extract_keywords(query)
    month_num = extract_month(query)
    matched_docs = []

    for doc in collection.find():
        if selected_location != "All" and doc.get("location", "").lower() != selected_location.lower():
            continue

        event_date = doc.get("date")
        if selected_month != "All" or month_num:
            if event_date:
                event_month = event_date.month
                if selected_month != "All" and event_month != selected_month:
                    continue
                if month_num and event_month != month_num:
                    continue

        match = False
        for kw in keywords:
            for field in ["title", "description", "location", "target_group"]:
                if fuzzy_match(str(doc.get(field, "")), kw):
                    match = True
                    break
            if match:
                break

        if match:
            matched_docs.append(doc)

    return matched_docs

def format_roles(matches):
    if not matches:
        return "No matching roles found."
    return "\n\n".join([
        f"📌 **Title**: {doc.get('title', 'N/A')}\n"
        f"📝 **Description**: {doc.get('description', 'No description')}\n"
        f"📍 **Location**: {doc.get('location', 'Unknown')}\n"
        f"📅 **Date**: {str(doc.get('date', 'No date'))[:10]}\n"
        f"📲 **WhatsApp Group**: [{doc.get('whatsappGroupLink', 'Join Link')}]" if doc.get('whatsappGroupLink') else "Not Provided"
        for doc in matches
    ])

# LangChain prompt template (updated)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Volunteer Connect Assistant. ONLY respond using the volunteer event data provided below. Never guess or make up events."),
    ("user", "{query}")
])
llm = OllamaLLM(model="tinyllama")
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# Main logic
if input_txt:
    matches = search_roles(input_txt)

    with st.sidebar:
        st.subheader("📜 Raw MongoDB Matches")
        st.write(matches)

    formatted_data = format_roles(matches)

    final_prompt = (
        f"The user asked: \"{input_txt}\"\n\n"
        f"Matching events:\n\n{formatted_data}\n\n"
        f"Please summarize this using natural language."
    )

    response = chain.invoke({"query": final_prompt})
    st.markdown("### 🤖 Response")
    st.markdown(response)
