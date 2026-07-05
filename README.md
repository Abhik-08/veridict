# Veridict – AI Response Quality Evaluator Agent

An AI-powered platform for evaluating the quality of AI-generated responses using Retrieval-Augmented Generation (RAG) and a Multi-Agent Judging Pipeline.

Veridict analyzes AI responses across multiple quality dimensions, provides explainable reasoning, and generates a comprehensive evaluation verdict.

<img width="575" height="775" alt="Screenshot 2026-07-05 214625" src="https://github.com/user-attachments/assets/44edbbd3-207a-4989-af83-080832a02de7" />


---

## Project Overview

Large Language Models (LLMs) often produce responses that may be relevant but factually incorrect, incomplete, or hallucinated.

Veridict is designed to objectively evaluate AI-generated responses by combining semantic retrieval with specialized AI judge agents.

The platform aims to assist developers, researchers, educators, and organizations in assessing the reliability and quality of AI outputs.

---

## Current Progress

### Completed

- Research on AI response evaluation techniques
- High-Level System Architecture
- RAG Pipeline Design
- Multi-Agent System Design
- Agent Responsibilities
- Orchestration Flow
- Evaluation Scoring Design
- Project Folder Structure
- Evaluation Input Module (Frontend UI)

### In Progress

- FastAPI Backend Development
- PostgreSQL Integration
- Pinecone Vector Database Integration
- RAG Knowledge Base
- Judge Agent Implementation

---

## Features

### Current

- Modern React Frontend
- Responsive UI
- Evaluation Input Module
- Question Submission
- AI Response Submission
- Optional Reference Answer
- Optional PDF Upload



### Upcoming

- FastAPI Backend
- Gemini API Integration
- Google Embedding API
- Pinecone Semantic Search
- Multi-Agent Evaluation
- Explainable Scoring
- Evaluation Dashboard
- Batch Evaluation
- History Management

---

## System Architecture

```
User
    │
    ▼
React Frontend
    │
    ▼
FastAPI Backend
    │
    ├── Evaluation Input Module
    ├── Reference Knowledge Base & RAG
    ├── Multi-Agent Judging Pipeline
    ├── Scoring Module
    ├── Results Management
    └── Analytics Dashboard
    │
    ▼
External AI Services
    ├── Gemini API
    └── Google Embedding API
    │
    ▼
Data Layer
    ├── Pinecone
    └── PostgreSQL
```

---

## Multi-Agent Evaluation Pipeline

The evaluation process consists of specialized AI agents:

- Relevance Judge
- Accuracy Judge
- Hallucination Detection Judge
- Completeness Judge
- Verdict Judge

Each agent independently evaluates a specific quality dimension before the Verdict Agent generates the final assessment.

---

## Evaluation Dimensions

- Relevance
- Accuracy
- Hallucination Detection
- Completeness
- Overall Verdict

---

## Tech Stack

### Frontend

- React
- Vite
- TypeScript
- Tailwind CSS

### Backend

- FastAPI
- Python
- Pydantic
- SQLAlchemy

### AI

- Gemini API
- Google Embedding API
- LangChain

### Database

- PostgreSQL
- Pinecone Vector Database

### PDF Processing

- pypdf

---

## Project Structure

```
veridict/

├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
│
├── backend/
│
├── docs/
│
├── README.md
│
└── .gitignore
```

---

## Development Roadmap

### Phase 1

- Research
- Architecture Design
- Evaluation Input Module

### Phase 2

- Backend Setup
- Database Configuration
- RAG Pipeline
- Semantic Retrieval

### Phase 3

- Multi-Agent Evaluation
- Scoring Engine
- Verdict Generation

### Phase 4

- Dashboard
- Deployment
- Performance Optimization

---

## Getting Started

### Clone Repository

```bash
git clone https://github.com/Abhik-08/veridict.git
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Future Enhancements

- Batch Response Evaluation
- Evaluation History
- Analytics Dashboard
- Export Reports
- Multiple LLM Support
- Advanced Explainability

---

## Author

**Abhik Mukherjee**

B.Tech Computer Science & Engineering  
Dr. B. C. Roy Engineering College

AI Intern – Infosys Springboard Virtual Internship (Batch 1)

Project: **Veridict – AI Response Quality Evaluator Agent**

---

## License

This project is developed as part of the Infosys Springboard Virtual Internship Program.
