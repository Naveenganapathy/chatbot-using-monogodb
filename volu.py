from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
from pymongo import MongoClient
import streamlit as st
from dotenv import load_dotenv
import os
import re
from datetime import datetime

# Load env vars
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

# Streamlit UI
st.title("🤖 Volunteer Connect Show Chat Bot")
input_txt = st.text_input("💬 Please enter your queries here...")

# Mongo connection
client = MongoClient(mongo_uri)
db = client["volunteer"]
collection = db["volunteer_roles"]

# Month keywords mapping
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

def search_roles(query):
    keywords = re.findall(r'\w+', query.lower())
    regex_clauses = []
    fields = ['title', 'description', 'location', 'target_group']

    for kw in keywords:
        for field in fields:
            regex_clauses.append({field: {"$regex": kw, "$options": "i"}})

    # Month-based date filter
    month_num = extract_month(query)
    if month_num:
        current_year = datetime.now().year
        date_filter = {
            "date": {
                "$gte": datetime(current_year, month_num, 1),
                "$lt": datetime(current_year, month_num % 12 + 1, 1)
            }
        }
        return list(collection.find({
            "$and": [
                {"$or": regex_clauses},
                date_filter
            ]
        }))
    else:
        return list(collection.find({"$or": regex_clauses}))

def format_roles(matches):
    return "\n\n".join([
        f"📌 **{doc.get('title', 'N/A')}**\n"
        f"📝 {doc.get('description', 'No description')}\n"
        f"📍 Location: {doc.get('location', 'Unknown')}\n"
        f"📅 Date: {str(doc.get('date', 'No date'))[:10]}\n"
        f"🔗 [Join WhatsApp]({doc.get('whatsappGroupLink', 'No link provided')})"
        for doc in matches
    ])

# LangChain setup
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Volunteer Connect Assistant. ONLY respond using the roles shown below. If none match, just say that. NEVER make up opportunities."),
    ("user", "{query}")
])
llm = OllamaLLM(model="tinyllama")
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# Main app logic
if input_txt:
    matches = search_roles(input_txt)

    with st.sidebar:
        st.subheader("🔍 Raw MongoDB Matches")
        st.write(matches)

    formatted_data = format_roles(matches) if matches else "❌ No matching roles found in the database."

    final_prompt = (
        f'The user asked: "{input_txt}"\n\n'
        f"Here are the matching volunteering roles from the database:\n\n"
        f"{formatted_data}\n\n"
        f"IMPORTANT: Use ONLY this data to answer the user\'s question. If no roles are relevant, say so clearly."
    )

    response = chain.invoke({"query": final_prompt})
    st.markdown(response)
