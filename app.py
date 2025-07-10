import os
import json
import base64
import pickle
import plotly.express as px
import faiss
import pandas as pd
from datetime import datetime
import streamlit as st
from sentence_transformers import SentenceTransformer
from embedder import embed_and_index
from ollama_client import query_ollama
from utils import chunk_text

# ---------- Paths ----------
doc_dir = "docs"
index_dir = "vector_stores"
faq_dir = "faqs"
announce_dir = "announcements"
feedback_file = "feedback/feedback.json"

for d in [doc_dir, index_dir, faq_dir, announce_dir, "feedback"]:
    os.makedirs(d, exist_ok=True)

# ---------- Background Styling ----------
def set_bg_and_style(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            font-family: 'Segoe UI', sans-serif;
            color: white;
        }}
        .main > div:nth-child(1) {{
            background-color: rgba(0, 0, 0, 0.6);
            padding: 2rem;
            border-radius: 15px;
            margin: 2rem;
            color: white;
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }}
        .stButton > button {{
            background-color: #ff4b4b;
            color: white;
            border-radius: 10px;
            padding: 8px 16px;
        }}
        </style>
    """, unsafe_allow_html=True)

set_bg_and_style("bg.jpg")

# ---------- Load Model ----------
@st.cache_resource
def get_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = get_model()
_ = model

# ---------- Session State ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.name = ""
    st.session_state.chat_history = {}

# ---------- Login ----------
if not st.session_state.logged_in:
    st.title(" Login")
    name = st.text_input("Enter your name")
    selected_role = st.selectbox("Select Role", ["employee", "hr", "manager"])
    if st.button("Login"):
        if name.strip() == "":
            st.warning("Please enter your name.")
            st.stop()
        st.session_state.logged_in = True
        st.session_state.name = name
        st.session_state.role = selected_role
        if selected_role not in st.session_state.chat_history:
            st.session_state.chat_history[selected_role] = []
        st.rerun()
    st.stop()

# ---------- Logout ----------
if st.sidebar.button(" Logout"):
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state.name = ""
    st.rerun()

# ---------- Sidebar Menu ----------
role_select = st.session_state.role
if role_select == "employee":
    selected_page = st.sidebar.radio(" Menu", ["Assistant", "Announcements", "FAQs", "Send Feedback"])
elif role_select == "hr":
    selected_page = st.sidebar.radio(" Menu", ["Assistant", "Upload Policy", "Post Announcement", "Add FAQ"])
elif role_select == "manager":
    selected_page = st.sidebar.radio(" Menu", ["Assistant", "View Feedback", "Analytics"])

st.title(" Internal Helpdesk Assistant")
st.markdown(f" Welcome **{st.session_state.name}**! You're logged in as **{role_select.upper()}**.")

# ---------- Page Logic ----------
if selected_page == "Announcements":
    st.subheader(" Announcements")
    for fname in sorted(os.listdir(announce_dir), reverse=True):
        with open(f"{announce_dir}/{fname}", "r") as f:
            st.markdown(f"""
            <div style='background-color:rgba(0,0,0,0.6); padding:10px; border-radius:10px; color:white;'>
            {f.read()}
            </div>
            """, unsafe_allow_html=True)

elif selected_page == "FAQs":
    st.subheader(" FAQs")
    for file in os.listdir(faq_dir):
        with open(f"{faq_dir}/{file}", "r") as f:
            faq = json.load(f)
            st.markdown(f"**Q:** {faq['q']}")
            st.markdown(f"**A:** {faq['a']}")

elif selected_page == "Send Feedback":
    st.subheader(" Send Feedback to Manager")
    fb = st.text_area("Feedback text")
    if st.button("Send Feedback"):
        entry = {
            "from": st.session_state.name,
            "role": role_select,
            "text": fb,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        feedbacks = []
        if os.path.exists(feedback_file):
            with open(feedback_file, "r") as f:
                feedbacks = json.load(f)
        feedbacks.append(entry)
        with open(feedback_file, "w") as f:
            json.dump(feedbacks, f, indent=2)
        st.success(" Feedback sent.")

elif selected_page == "Upload Policy":
    st.subheader(" Upload company policy PDF")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if uploaded_file:
        os.makedirs(doc_dir, exist_ok=True)
        save_path = os.path.join(doc_dir, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.read())

        # Save with prefix like hr_filename.index
        embed_and_index("hr", save_path)
        st.success(f"✅ Uploaded and indexed: {uploaded_file.name}")

    st.subheader(" Uploaded Files")
    existing_files = [f for f in os.listdir(doc_dir) if f.endswith(".pdf")]

    if existing_files:
        selected_file = st.selectbox("Uploaded Files", existing_files, key="uploaded_files_dropdown")
        if st.button(f"🗑️ Delete '{selected_file}'"):
            try:
                # Delete PDF
                file_path = os.path.join(doc_dir, selected_file)
                os.remove(file_path)

                # Delete vector index and chunk
                base_name = os.path.splitext(selected_file)[0]
                index_file = f"hr_{base_name}.index"
                chunk_file = f"hr_{base_name}_chunks.pkl"

                index_path = os.path.join(index_dir, index_file)
                chunk_path = os.path.join(index_dir, chunk_file)

                if os.path.exists(index_path):
                    os.remove(index_path)
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)

                st.success(f"✅ Deleted {selected_file} and its index files.")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error deleting file: {e}")
    else:
        st.info("No uploaded files found.")


elif selected_page == "Post Announcement":
    st.subheader(" Post Announcement")
    ann_text = st.text_area("Announcement text")
    if st.button("Post"):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        with open(f"{announce_dir}/{timestamp}.txt", "w") as f:
            f.write(ann_text)
        st.success(" Announcement posted.")

    st.subheader(" Delete Announcement")
    files = os.listdir(announce_dir)
    selected = st.selectbox("Select announcement to delete", files)
    if st.button("Delete Announcement"):
        os.remove(f"{announce_dir}/{selected}")
        st.success(" Deleted.")
        st.rerun()


elif selected_page == "Add FAQ":
    st.subheader(" Add FAQ")
    faq_q = st.text_input("Question")
    faq_a = st.text_area("Answer")
    if st.button("Add FAQ"):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        with open(f"{faq_dir}/{timestamp}.json", "w") as f:
            json.dump({"q": faq_q, "a": faq_a}, f)
        st.success(" FAQ added.")


    st.subheader(" Delete FAQ")
    faq_files = os.listdir(faq_dir)
    
    to_delete = st.selectbox("Select FAQ to delete", faq_files)
    if st.button("Delete FAQ"):
        os.remove(f"{faq_dir}/{to_delete}")
        st.success(" Deleted.")
        st.rerun()


elif selected_page == "View Feedback":
    st.subheader(" Employee Feedback")
    if os.path.exists(feedback_file):
        with open(feedback_file, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        st.dataframe(df)

        names = df['from'].tolist()
        index = st.selectbox("Select feedback to delete", range(len(names)))
        if st.button("Delete Feedback"):
            del data[index]
            with open(feedback_file, "w") as f:
                json.dump(data, f, indent=2)
            st.success(" Deleted.")
            st.rerun()

    else:
        st.info("No feedback found.")

#if st.sidebar.radio("Menu", ["Assistant", "View Feedback", "Analytics"]) == "Analytics":
elif selected_page == "Analytics":
    st.subheader(" Feedback Analytics Dashboard")

    if os.path.exists(feedback_file):
        with open(feedback_file, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)

        st.markdown(f"**Total Feedbacks:** `{len(df)}`")

        top_user = df["from"].value_counts().idxmax()
        top_count = df["from"].value_counts().max()
        st.markdown(f"**Top Contributor:** `{top_user}` with `{top_count}` feedbacks")

        # --- Visualization ---
        feedback_counts = df["from"].value_counts().reset_index()
        feedback_counts.columns = ["User", "Feedback Count"]

        donut = px.pie(feedback_counts, names="User", values="Feedback Count", hole=0.5,
                       title="Feedback Share by Role")
        st.plotly_chart(donut, use_container_width=True)

        bar = px.bar(feedback_counts, x="User", y="Feedback Count", color="User",
                     title="Feedback Count by User", text="Feedback Count")
        st.plotly_chart(bar, use_container_width=True)

        # --- Example Preview ---
        st.subheader(" Recent Feedback Examples")
        for _, row in df.tail(3).iterrows():
            msg = row.get('message') or row.get('text') or row.get('feedback') or "No message"
            st.markdown(f"- **{row['from']}**: _\"{msg[:100]}...\"_")

    else:
        st.info("No feedback to analyze.")


if selected_page == "Assistant":
    st.subheader(" Chat with Assistant")
    user_input = st.text_input("You:", key="user_input")
    if user_input:
        try:
            context = ""
            q_embed = model.encode([user_input], show_progress_bar=False)

            # Search all index files (e.g. hr_policy1.index, manager_rules.index)
            index_files = [f for f in os.listdir(index_dir) if f.endswith(".index")]
            st.write("🔍 Found index files:", index_files)  # Debug line


            for index_file in index_files:
                try:
                    index_path = os.path.join(index_dir, index_file)
                    base_name = index_file.replace(".index", "")
                    chunk_path = os.path.join(index_dir, f"{base_name}_chunks.pkl")
            
                    index = faiss.read_index(index_path)
                    with open(chunk_path, "rb") as f:
                        chunks = pickle.load(f)
            
                    if not chunks:
                        st.warning(f"⚠️ No chunks found in {chunk_path}")
                        continue
            
                    D, I = index.search(q_embed, k=1)
                    if I is not None and I[0][0] != -1:
                        top_context = "\n".join([chunks[i] for i in I[0] if i < len(chunks)])
                        context += f"\n--- From {index_file} ---\n{top_context}\n"
                    else:
                        st.warning(f"⚠️ No matching result found in: {index_file}")
                except Exception as e:
                    st.error(f"❌ Error reading {index_file}: {e}")

            if context.strip() == "":
                st.warning("⚠️ No relevant context found in any index.")
                st.stop()

            prompt = f"""
            User Role: {role_select}
            Context from all policies:
            {context}
            Question: {user_input}
            Answer:
            """
            with st.spinner("Thinking..."):
                answer = query_ollama(prompt)
            st.session_state.chat_history[role_select].append((user_input, answer))
            st.markdown(f"**Assistant:** {answer}")
        except:
            st.error("❌ No indexed documents found. Please upload policies.")

    if st.session_state.chat_history.get(role_select):
        with st.sidebar.expander(" Chat History"):
            for q, a in st.session_state.chat_history[role_select]:
                st.markdown(f"**You:** {q}")
                st.markdown(f"**Assistant:** {a}")
