# Custom FastAPI Server for Qwen Marketing

This directory contains a custom FastAPI server that wraps the Qwen Marketing model using vLLM.

## Project Structure

```
custom_server/
├── main.py            # FastAPI application
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Setup

1. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Or run directly:
   ```bash
   python main.py
   ```

## API Endpoints

### Generate Text
- **POST** `/generate`
  - Generate marketing content using the Qwen Marketing model
  - **Request Body**:
    ```json
    {
      "prompt": "Write a marketing campaign for a new product",
      "max_tokens": 1024,
      "temperature": 0.7,
      "top_p": 1.0
    }
    ```
  - **Response**:
    ```json
    {
      "status": "success",
      "generated_text": "[Generated text will appear here]",
      "model": "marketeam/Qwen-Marketing"
    }
    ```

### Health Check
- **GET** `/health`
  - Check if the server is running
  - Returns: `{"status": "healthy", "model": "marketeam/Qwen-Marketing"}`

## Environment Variables

No environment variables are required by default, but you can configure:
- `MODEL_NAME`: Override the default model (default: "marketeam/Qwen-Marketing")
- `PORT`: Server port (default: 8000)
