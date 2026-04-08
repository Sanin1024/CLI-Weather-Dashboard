# 🌦️ CLI Weather Dashboard

A **production-quality, feature-rich command-line application** for retrieving and visualizing real-time weather data with an elegant terminal interface.  
Built using **Python** and powered by the **OpenWeatherMap API**, this tool delivers fast, reliable, and visually structured weather insights directly in the CLI.

---

## 🌟 Key Features

### 🌍 Weather Data
- **Real-Time Weather**: Retrieve current weather conditions for any city worldwide  
- **5-Day Forecasts**: Detailed forecasts including temperature trends, daily highs/lows, and precipitation probability  

### 📍 Regional Intelligence
- **Kerala District Support**: Weather data for all 14 districts  
- **Indian State Summaries**: Aggregated insights for major states such as Maharashtra, Karnataka, Tamil Nadu, and Delhi  

### 🧠 Smart Capabilities
- **IP-Based Geolocation**: Automatic location detection for instant weather access  
- **Persistent Preferences**: Save default city and favorite locations  
- **Intelligent Caching**: 10-minute TTL cache with optional force refresh  
- **Parallel API Requests**: Optimized performance using concurrent data fetching  

### 🎨 Terminal Experience
- **Rich CLI Interface**: Structured tables, layouts, and ASCII-based visual trends using the Rich library  
- **Comprehensive Error Handling**: Clear and informative messages for API errors, invalid inputs, and network issues  

---

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher  
- pip package manager  

### From GitHub (Recommended)
```bash
git clone https://github.com/Sanin1024/CLI-Weather-Dashboard.git
cd CLI-Weather-Dashboard
pip install -e .
