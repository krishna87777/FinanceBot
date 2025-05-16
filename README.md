# Indian Stock Dashboard

## Overview
The Indian Stock Dashboard is a powerful web application built with Streamlit that provides real-time data, analysis, and insights on Indian stocks and market indices. The dashboard fetches data from Screener.in and allows users to search, analyze, and visualize stock information with interactive charts. It also features an AI-powered financial advisor to answer user queries about stocks and market trends.

![Dashboard Preview](https://via.placeholder.com/800x400?text=Indian+Stock+Dashboard)

## Features

### 📊 Market Data
- **Real-time stock information** for Indian companies and indices
- **Interactive price charts** with customizable time periods (1M, 6M, 1Yr, 3Yr, 5Yr, 10Yr, Max)
- **Technical indicators** including 50-day and 200-day moving averages
- **Key financial metrics** displayed in an easy-to-read format:
  - Market cap, P/E ratio, Price to Book value
  - Dividend yield
  - 1-year, 5-year, and 10-year CAGR
  - 52-week high/low
- **Company information** including sector and business description

### 📰 Latest News
- **Real-time financial news** aggregated from Economic Times
- **News summaries** with links to full articles

### 🤖 AI Financial Advisor
- **OpenAI-powered assistant** to answer questions about stocks and markets
- **Contextual awareness** of the currently selected stock
- **Custom financial insights** based on user queries

### 🔍 Search & Navigation
- **Company search** functionality with auto-suggestions
- **Quick access** to popular Indian stocks and major indices
- **Direct input** of stock symbols

## Installation

### Prerequisites
- Python 3.7+
- pip

### Setup
1. Clone the repository:
   ```
   git clone https://github.com/krishna87777/FinanceBot
   cd indian-stock-dashboard
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key (for AI Advisor feature):
   - Option 1: Set as environment variable:
     ```
     export OPENAI_API_KEY=your_api_key_here  # On Windows: set OPENAI_API_KEY=your_api_key_here
     ```
   - Option 2: Input directly in the app when prompted

## Usage

### Running the Dashboard
1. Start the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Access the dashboard in your web browser at `http://localhost:8501`

### Using the Dashboard
1. **Search for a stock** using the search box or enter a ticker symbol directly
2. **View stock data** in the Market Data tab
3. **Analyze price trends** using the interactive charts
4. **Check latest news** in the News tab
5. **Ask questions** about the selected stock in the AI Advisor tab

## Data Sources
- Stock data is fetched from [Screener.in](https://www.screener.in/)
- Financial news is sourced from [Economic Times](https://economictimes.indiatimes.com/)

## Limitations
- Free tier usage of OpenAI API limits the number of AI Advisor queries
- News aggregation may be affected by source website changes
- Some financial metrics might not be available for all companies

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements
- [Streamlit](https://streamlit.io/) for the web app framework
- [Plotly](https://plotly.com/) for interactive charts
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for web scraping
- [OpenAI](https://openai.com/) for the AI advisor functionality
- [Screener.in](https://www.screener.in/) for financial data
