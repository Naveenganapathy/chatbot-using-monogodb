from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
import streamlit as st
import re
from datetime import datetime

# Streamlit UI
st.title("🤖 Volunteer Connect Show Chat Bot")
input_txt = st.text_input("💬 Please enter your queries here...")

# Month keywords mapping
MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12
}

# Static volunteer role data (flattened and corrected)
volunteer_roles = [
    {
        "role": "Event Coordinator",
        "organization": "Green Earth NGO",
        "location": "Chennai",
        "date": "2025-05-15",
        "description": "Help organize an environmental awareness event.",
        "volunteer_type": "In-person",
        "contact": "greenearth@ngo.org"
    },
    {
        "role": "Food Distribution Volunteer",
        "organization": "Chennai Food Relief",
        "location": "Chennai",
        "date": "2025-05-30",
        "description": "Distribute food to the homeless and low-income families.",
        "volunteer_type": "In-person",
        "contact": "chennaifoodrelief@ngo.org"
    },
    {
        "role": "Donation Sorting Volunteer",
        "organization": "Hope for All",
        "location": "Chennai",
        "date": "2025-05-30",
        "description": "Sort and organize donations for underprivileged communities.",
        "volunteer_type": "In-person",
        "contact": "hopeforall@ngo.org"
    },
    {
        "role": "Community Cleanup Volunteer",
        "organization": "Clean Chennai Mission",
        "location": "Chennai",
        "date": "2025-05-18",
        "description": "Participate in beach and public park clean-up activities.",
        "volunteer_type": "In-person",
        "contact": "info@cleanchennai.org"
    },
    {
        "role": "Senior Care Assistant",
        "organization": "Golden Age Home",
        "location": "Chennai",
        "date": "2025-05-20",
        "description": "Spend time with elderly residents and assist with daily activities.",
        "volunteer_type": "In-person",
        "contact": "volunteer@goldenage.org"
    },
    {
        "role": "Literacy Program Tutor",
        "organization": "Read to Lead Foundation",
        "location": "Chennai",
        "date": "2025-06-01",
        "description": "Teach reading and writing to underprivileged children.",
        "volunteer_type": "In-person",
        "contact": "contact@readtolead.org"
    },
    {
        "role": "Blood Donation Camp Organizer",
        "organization": "Chennai Health Initiative",
        "location": "Chennai",
        "date": "2025-06-05",
        "description": "Help coordinate logistics for a city-wide blood donation drive.",
        "volunteer_type": "In-person",
        "contact": "health@chi.org"
    },
    {
        "role": "Animal Shelter Helper",
        "organization": "Pet Haven",
        "location": "Chennai",
        "date": "2025-05-25",
        "description": "Assist in feeding, cleaning, and playing with rescued animals.",
        "volunteer_type": "In-person",
        "contact": "volunteer@pethaven.in"
    },
    {
        "role": "Child Welfare Assistant",
        "organization": "Smiles for Kids",
        "location": "Chennai",
        "date": "2025-05-29",
        "description": "Organize fun learning sessions for orphaned children.",
        "volunteer_type": "In-person",
        "contact": "hello@smilesforkids.org"
    },
    {
        "role": "Tree Plantation Drive Volunteer",
        "organization": "Green Roots India",
        "location": "Chennai",
        "date": "2025-06-10",
        "description": "Participate in sapling planting across urban areas.",
        "volunteer_type": "In-person",
        "contact": "greenroots@india.org"
    },
    {
        "role": "Health Awareness Campaign Volunteer",
        "organization": "LifeLine Chennai",
        "location": "Chennai",
        "date": "2025-05-21",
        "description": "Distribute pamphlets and spread awareness about hygiene and health.",
        "volunteer_type": "In-person",
        "contact": "connect@lifeline.org"
    },
    {
        "role": "Youth Mentor",
        "organization": "Bright Futures NGO",
        "location": "Chennai",
        "date": "2025-06-15",
        "description": "Mentor high school students on career and life skills.",
        "volunteer_type": "In-person",
        "contact": "mentor@brightfutures.org"
    },
    {
        "role": "Event Photographer",
        "organization": "Smile Events",
        "location": "Chennai",
        "date": "2025-05-30",
        "description": "Capture moments from a community service event.",
        "volunteer_type": "In-person",
        "contact": "photos@smileevents.in"
    },
    {
        "role": "Online Content Creator",
        "organization": "Hope Digital",
        "location": "Chennai",
        "date": "2025-06-01",
        "description": "Create blog and social media content to promote causes.",
        "volunteer_type": "Remote",
        "contact": "digital@hope.org"
    },
    {
        "role": "First Aid Support Volunteer",
        "organization": "Emergency Response Team",
        "location": "Chennai",
        "date": "2025-05-28",
        "description": "Assist medical staff during community events.",
        "volunteer_type": "In-person",
        "contact": "support@ertchennai.in"
    },
    {
        "role": "Workshop Facilitator",
        "organization": "SkillUp Chennai",
        "location": "Chennai",
        "date": "2025-06-12",
        "description": "Conduct workshops on resume writing and interview prep.",
        "volunteer_type": "In-person",
        "contact": "facilitator@skillup.org"
    },
    {
        "role": "Tech Support Volunteer",
        "organization": "Digital Literacy Mission",
        "location": "Chennai",
        "date": "2025-05-26",
        "description": "Teach basic computer skills to the elderly and women.",
        "volunteer_type": "In-person",
        "contact": "tech@dlm.org"
    },
    {
        "role": "Event Host",
        "organization": "Youth Action",
        "location": "Chennai",
        "date": "2025-05-31",
        "description": "Host a youth-led community dialogue event.",
        "volunteer_type": "In-person",
        "contact": "youth@ya.org"
    },
    {
        "role": "Disaster Relief Volunteer",
        "organization": "ReliefNow Foundation",
        "location": "Chennai",
        "date": "2025-06-05",
        "description": "Assist in packing and distributing relief kits to flood-affected families.",
        "volunteer_type": "In-person",
        "contact": "relief@reliefnow.org"
    },
    {
        "role": "Library Assistant",
        "organization": "Books for All",
        "location": "Chennai",
        "date": "2025-06-03",
        "description": "Help organize books and manage reading sessions for children.",
        "volunteer_type": "In-person",
        "contact": "library@booksforall.org"
    },
    {
        "role": "Social Media Volunteer",
        "organization": "Voice for Voiceless",
        "location": "Chennai",
        "date": "2025-06-08",
        "description": "Create awareness campaigns for animal rights online.",
        "volunteer_type": "Remote",
        "contact": "voice@vfv.org"
    },
    {
        "role": "Art Therapy Assistant",
        "organization": "Healing Brushes",
        "location": "Chennai",
        "date": "2025-05-22",
        "description": "Help organize art therapy sessions for children with trauma.",
        "volunteer_type": "In-person",
        "contact": "art@healingbrushes.org"
    },
    {
        "role": "Fundraising Volunteer",
        "organization": "Support India Trust",
        "location": "Chennai",
        "date": "2025-06-07",
        "description": "Engage donors and help raise funds for health programs.",
        "volunteer_type": "Remote",
        "contact": "fundraise@supportindia.in"
    }
]

# Helper functions
def extract_month(query):
    for month, num in MONTH_MAP.items():
        if month in query.lower():
            return num
    return None

def search_roles(query):
    keywords = re.findall(r'\w+', query.lower())
    month_num = extract_month(query)

    matched = []
    for role in volunteer_roles:
        text_blob = f"{role['role']} {role['description']} {role['location']} {role['organization']}".lower()
        if any(kw in text_blob for kw in keywords):
            if month_num:
                date_obj = datetime.strptime(role['date'], "%Y-%m-%d")
                if date_obj.month == month_num:
                    matched.append(role)
            else:
                matched.append(role)
    return matched

def format_roles(matches):
    return "\n\n".join([
        f"📌 **{r['role']}**\n"
        f"🏢 Organization: {r['organization']}\n"
        f"📝 {r['description']}\n"
        f"📍 Location: {r['location']}\n"
        f"📅 Date: {r['date']}\n"
        f"📧 Contact: {r['contact']}"
        for r in matches
    ])

# LangChain setup
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Volunteer Connect Assistant. ONLY respond using the roles shown below. If none match, say so. NEVER make up events."),
    ("user", "{query}")
])
llm = OllamaLLM(model="tinyllama")
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# Main logic
if input_txt:
    matches = search_roles(input_txt)

    with st.sidebar:
        st.subheader("🔍 Matched Roles")
        if matches:
            for match in matches:
                st.write(f"🔹 {match['role']} - {match['organization']} on {match['date']}")
        else:
            st.write("❌ No matching roles found.")

    formatted = format_roles(matches) if matches else "❌ No matching roles found."

    final_prompt = (
        f'The user asked: "{input_txt}"\n\n'
        f"Here are the matching volunteering roles from the database:\n\n"
        f"{formatted}\n\n"
        f"IMPORTANT: Use ONLY this data to answer. If no match is relevant, say so clearly."
    )

    response = chain.invoke({"query": final_prompt})
    st.markdown(response)
