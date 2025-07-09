# 🧠 Internal Helpdesk Assistant

A role-based, AI-powered internal helpdesk assistant that enables employees, HR, and managers to interact with company policies, FAQs, announcements, and document approvals via a conversational interface.

---

## 🚀 Project Overview

The **Internal Helpdesk Assistant** is an intelligent chatbot system designed to streamline internal communication within organizations. It allows users (employees, HR, and managers) to interact with documents using natural language queries. It uses **FAISS** for vector-based document retrieval and **Ollama LLM** for contextual response generation.

---

## 🎯 Key Features

### ✅ Common Features
- 🔍 **Document Search via Chat** – Ask questions and get context-aware answers based on uploaded PDF documents.
- 💬 **LLM-Driven Conversations** – Powered by Ollama (offline-capable local LLM).
- 📁 **Role-Based File Upload** – Each user role (Employee, HR, Manager) can upload and access relevant documents.
- 🔄 **Persistent File Storage** – Uploaded PDFs are indexed and stored for future queries.

### 👨‍💼 Employee Role
- Ask queries from all uploaded employee policy documents.
- View HR announcements.
- Submit feedback to HR.

### 🧑‍💼 HR Role
- Upload company policies.
- Upload & manage FAQs.
- Post announcements.
- View feedback analytics.
- Track user queries.

### 👩‍💼 Manager Role
- Access policy documents for approval.
- Approve or reject uploaded policies.
- View employee feedback.
- Access announcement board.

---

## ⚙️ Tech Stack

| Component            | Tech Used                                |
|----------------------|-------------------------------------------|
| Frontend             | Streamlit                                 |
| Backend              | FastAPI                                   |
| LLM                  | Ollama (e.g., Mistral, Gemma)              |
| Embedding Model      | Sentence Transformers (BERT-based)        |
| Vector DB            | FAISS                                     |
| OCR (Optional)       | Tesseract / EasyOCR (if used in future)   |
| Storage              | JSON & local file system                  |

---

## 🗂️ Folder Structure

```
├── app.py                 # Main Streamlit app
├── embedder.py           # Handles embedding and FAISS indexing
├── ollama_client.py      # LLM query handler (Ollama)
├── utils.py              # Chunking and helper functions
├── /docs                 # Uploaded PDFs (per role)
├── /vector_stores        # FAISS index files
├── /faqs                 # FAQ .json files
├── /announcements        # Announcement .txt files
├── /feedback             # Feedback stored as .json
```

---

## 🔄 Document Handling

- PDFs uploaded per role are **chunked**, **embedded**, and **indexed** using FAISS.
- Each role’s documents are queried independently to ensure privacy and relevance.
- All chat queries are transformed into embeddings and matched against FAISS index to find the most relevant context.

---

## 🧠 How LLM Works (Ollama)

- Ollama runs a local language model like `mistral` or `gemma`.
- For each user query:
  1. Convert query to vector using SentenceTransformer.
  2. Retrieve top-k relevant chunks using FAISS.
  3. Provide retrieved context + query to Ollama.
  4. Ollama generates a human-like, context-aware response.

---

## 📊 Analytics & Feedback

- Feedbacks are stored in a JSON file and visualized using bar charts.
- HR can monitor who submitted feedback and analyze query patterns.

---

## ⚡ Performance Optimization

- Lightweight models like `mistral:7b` used via Ollama for faster responses.
- Chunking and indexing are optimized for quick search (<2 seconds).
- Support added for handling **multiple PDFs per role** with duplicate file handling.

---

## 📌 Future Enhancements

- [x] Role-based query filtering
- [x] HR FAQ upload system
- [x] HR announcement management
- [x] Manager approval workflow
- [ ] Email/chat alerts on policy updates
- [ ] Mobile interface with React Native
- [ ] Smart reminders for policy expiry

---

## 🛠️ Setup Instructions

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start Ollama**
   ```bash
   ollama run mistral
   ```

3. **Run the Streamlit app**
   ```bash
   streamlit run app.py
   ```

4. **Upload PDFs per role and begin chatting!**

---

## 🧾 Credits

Developed by **Gurupriya Kannan**  
Role: *AI/ML Developer | Data Analyst | Frontend Developer*  
Portfolio: [https://gurupriyak03.github.io/Portfolio/](#)    
LinkedIn: [https://www.linkedin.com/in/gurupriyakannan03/](#)