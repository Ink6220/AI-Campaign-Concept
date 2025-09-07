# 🚀 Qwen Marketing Campaign Generator

A powerful AI-powered marketing campaign generation system built with Python, FastAPI, and Qwen AI. This tool helps you create data-driven marketing campaigns tailored to your business objectives.

## 🏗️ Project Structure

```
qwen-market/
├── Front/                    # Frontend React application
│   └── src/
│       └── App.tsx          # Main React component
├── qwen_market/             # Backend Python package
│   ├── __init__.py         # Package initialization
│   ├── models.py          # Pydantic models and data structures
│   ├── prompts.py         # AI prompt templates
│   ├── orchestrator.py    # Campaign generation logic
│   └── services/
│       └── agents.py      # AI agent implementations
├── api.py                 # FastAPI application
├── main.py               # Example usage
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- pip (Python package manager)
- npm or yarn (Node package manager)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd qwen-market
   ```

2. **Set up vLLM Server**
   The vLLM server provides a built-in HTTP API for model inference. Start it with:
   ```bash
   vllm serve marketeam/Qwen-Marketing --host 0.0.0.0 --port 8080 --max-model-len 4096
   ```
   
   This starts vLLM's built-in server (not FastAPI or Flask) with the following endpoints:
   - `POST /v1/completions` - For text generation
   - `GET /v1/health` - Health check endpoint
   
   Configure your application to use this server by setting in your `.env` file:
   ```
   OPENAI_BASE_URL=http://localhost:8080/v1
   ```
   
   The API will be available at `http://localhost:8080`
   
   ### Alternative: Custom FastAPI Deployment
   
   If you need custom API endpoints, you can create a FastAPI wrapper around vLLM:
   
   ```python
   from fastapi import FastAPI
   from vllm import AsyncLLMEngine
   import uvicorn
   
   app = FastAPI()
   engine = AsyncLLMEngine("marketeam/Qwen-Marketing")
   
   @app.post("/generate")
   async def generate(prompt: str):
       output = await engine.generate(prompt)
       return {"result": output}
   
   if __name__ == "__main__":
       uvicorn.run(app, host="0.0.0.0", port=8000)
   ```
   
   Then run with:
   ```bash
   python custom_server.py
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the FastAPI server**
   ```bash
   uvicorn api:app --reload
   ```
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to the frontend directory**
   ```bash
   cd Front
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

## 🌐 API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

### Main Endpoints

#### 1. Generate Campaign
- **POST** `/generate-campaign`
  - Generates a new marketing campaign based on provided parameters
  - Accepts JSON payload with campaign details
  - Returns the generated campaign in JSON format

#### 2. Regenerate Campaign
- **POST** `/regenerate-campaign`
  - Regenerates a campaign with modified parameters
  - Useful for refining previous campaign results

## 🛠️ Example API Request

```python
import requests
import json

url = "http://localhost:8000/generate-campaign"
payload = {
    "industry": "Fashion Retail",
    "target_audience": {
        "age": "18-35",
        "location": "Urban areas",
        "lifestyle": "Fashion-conscious, social media active"
    },
    "genders": ["men", "women"],
    "budget_range": "Medium (฿50,000-100,000)",
    "campaign_objective": "Brand Awareness",
    "constraints": "Must be family-friendly",
    "additional_comments": "Focus on sustainable fashion"
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

## 🧪 Testing

### Backend Tests
```bash
pytest
```

### Frontend Tests
```bash
cd Front
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Qwen AI for the powerful language model
- FastAPI for the awesome web framework
- All contributors who helped improve this project
           "location": "City",
           "lifestyle": "Target Lifestyle"
         },
         "budget_range": "500,000 THB",
         "campaign_objective": "Your Objective"
       }"""
       
       results = await orchestrator(user_prompt)
       return results
   
   # Run the async function
   results = asyncio.run(run_campaign())
   ```

## Configuration

Make sure to set up your OpenAI API configuration:
- Update the `base_url` in `qwen_market/services/agents.py` if needed
- Set any required environment variables

## License

MIT
