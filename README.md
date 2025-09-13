# Property Advisor Agent

A Streamlit-based property search and recommendation system powered by LangChain and various LLM providers.

## Features

- **Intelligent Property Search**: Uses hybrid search combining semantic and keyword-based retrieval
- **Multiple View Modes**: Cards, Table, and Grid views for property listings
- **Detailed Property Information**: Comprehensive property details including specifications, facilities, and descriptions
- **LLM-Powered Query Processing**: Advanced intent detection and field extraction

## Setup for Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Property-Advisor-Agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory with:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   MISTRAL_API_KEY=your_mistral_api_key_here  # Optional
   PINECONE_API_KEY=your_pinecone_api_key_here  # Optional
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## Deployment on Streamlit Cloud

1. **Push your code to GitHub**
   - Make sure all files are committed and pushed to your repository

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Set the main file path to `app.py`

3. **Configure secrets**
   - In your Streamlit Cloud app settings, go to "Secrets"
   - Add the following secrets:
     ```
     GROQ_API_KEY = "your_groq_api_key_here"
     MISTRAL_API_KEY = "your_mistral_api_key_here"  # Optional
     PINECONE_API_KEY = "your_pinecone_api_key_here"  # Optional
     ```

4. **Deploy**
   - Click "Deploy" and wait for the deployment to complete

## Required API Keys

- **GROQ_API_KEY**: Required for LLM functionality (get from [console.groq.com](https://console.groq.com))
- **MISTRAL_API_KEY**: Optional, for additional LLM models (get from [console.mistral.ai](https://console.mistral.ai))
- **PINECONE_API_KEY**: Optional, for vector search functionality (get from [app.pinecone.io](https://app.pinecone.io))

## Usage

1. Enter your API keys in the sidebar
2. Type your property search query in the text input
3. Click "Search" to find relevant properties
4. Browse results in different view modes (Cards, Table, Grid)
5. Click "Let's Explore →" on any property for detailed information

## File Structure

- `app.py`: Main Streamlit application
- `main.py`: Core workflow orchestration
- `llm_models.py`: LLM model initialization and management
- `intent_detection_agent.py`: Intent detection and response handling
- `csv_agent.py`: CSV data processing and filtering
- `hybrid_search.py`: Hybrid search functionality
- `checklist_agent.py`: Field extraction and validation
- `query_for_hybrid.py`: Query processing for hybrid search
- `dataset/`: Property data files
- `.streamlit/config.toml`: Streamlit configuration

## Troubleshooting

- **Import errors**: Make sure all dependencies are installed correctly
- **API key errors**: Verify your API keys are correct and have sufficient credits
- **Memory issues**: The app uses caching to optimize performance, but large datasets may require more memory
