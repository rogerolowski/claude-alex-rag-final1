# LEGO AI Assistant

[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/rogerolowski/claude-alex-rag-final1)

A Streamlit-based AI assistant for LEGO collectors that combines multiple LEGO APIs with semantic search and AI-powered responses.

## Features

- **Multi-API Integration**: Connects to Brickset, Rebrickable, and BrickOwl APIs
- **Semantic Search**: Uses ChromaDB for intelligent LEGO set searching
- **AI-Powered Responses**: Leverages OpenAI GPT-4 for contextual answers
- **Data Storage**: SQLite database for structured data storage
- **Modern UI**: Clean Streamlit interface for easy interaction

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- API keys for:
  - OpenAI
  - Brickset
  - Rebrickable
  - BrickOwl

### Environment Setup

1. Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_key
BRICKSET_API_KEY=your_brickset_key
REBRICKABLE_API_KEY=your_rebrickable_key
BRICKOWL_API_KEY=your_brickowl_key
```

### Running the Application

#### Using Docker (Recommended)
```bash
docker-compose up --build
```

#### Using Python directly
```bash
cd app
pip install -r requirements.txt
streamlit run main.py
```

The application will be available at `http://localhost:8501`

## Project Structure

```
├── /app
│   ├── main.py                 # Streamlit app and main entry point
│   ├── data_layer.py          # SQLite and ChromaDB logic
│   ├── api_layer.py           # Unified LEGO API interface
│   ├── ai_layer.py            # LangChain and OpenAI integration
│   ├── models.py              # Pydantic models for data validation
│   └── requirements.txt        # Python dependencies
├── .gitpod.yml                # Gitpod configuration
├── docker-compose.yml         # Docker Compose configuration
└── Dockerfile                 # Docker image for the app
```

## Development

This project uses:
- **Streamlit** for the web interface
- **LangChain** for AI integration
- **ChromaDB** for semantic search
- **SQLite** for data storage
- **Pydantic** for data validation

## License

[Add your license information here] 