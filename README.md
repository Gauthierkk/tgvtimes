# 🚄 TGV Times

A Streamlit web application for viewing European high-speed train schedules in real-time using the Navitia API. Works like a train station departure/arrival board!

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.50+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features

- 🚉 **Station Board View**: View departures or arrivals at any station, just like a real station board
- 🛫 **Departures/Arrivals Toggle**: Switch between trains leaving or arriving at your selected station
- 🔍 **Smart Filtering**: Filter by destination (departures) or origin (arrivals) station
- 🌍 **International Routes**: Supports TGV Lyria (Switzerland), Eurostar (UK), and more
- 🔢 **Train Number Search**: Look up specific trains by number
- 📅 **Date & Time Filters**: Search for trains on specific dates and times
- 🔄 **Auto-Reload**: Automatically refreshes results when filters change
- ⏱️ **Real-Time Delays**: Shows departure and arrival delays
- 📊 **Journey Statistics**: View on-time performance and average delays
- 🎨 **Clean UI**: Responsive Streamlit interface with color-coded status indicators

## Demo

![TGV Times Dashboard](https://via.placeholder.com/800x400?text=TGV+Times+Dashboard+Screenshot)

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) - Interactive web application framework
- **Backend**: [Navitia SNCF API](https://doc.navitia.io/) - Real-time French train data
- **Package Manager**: [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- **Code Quality**: [Ruff](https://github.com/astral-sh/ruff) - Fast Python linter and formatter

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- SNCF API key from [Navitia](https://www.navitia.io/)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Gauthierkk/tgvtimes.git
cd tgvtimes
```

### 2. Install Dependencies

```bash
# Install all dependencies using uv
make install

# Or manually:
uv sync --all-extras
```

### 3. Configure API Key

Create a `.env` file in the project root:

```bash
touch .env
```

Add your SNCF API key:

```env
SNCF_API_KEY=your_api_key_here
```

**How to get an API key:**
1. Visit [Navitia.io](https://www.navitia.io/)
2. Sign up for a free account
3. Go to "My Applications" and create a new app
4. Copy your API key

## Usage

### Running Locally

```bash
# Using Make
make app

# Or directly with Streamlit
streamlit run src/frontend/app.py
```

The application will open in your browser at `http://localhost:8501`

### Using the Application

#### Station Board Mode (Default)
View trains at a station like a real departure/arrival board:

1. **Select a Station**: Choose any station (e.g., "Paris Gare de Lyon")
2. **Choose View**: Toggle between "Departures" or "Arrivals"
3. **Filter (Optional)**:
   - For departures: Filter by destination station
   - For arrivals: Filter by origin station
   - Select "All" to see all trains
4. **Set Date/Time**: Choose your travel date and optional time filter
5. **Filter by Provider**: Choose specific operators (TGV INOUI, Eurostar, etc.) or "All"
6. Results update automatically when you change any filter

**Example**: View all Eurostar departures from Paris Gare du Nord to London:
- Station: Paris Gare du Nord
- View: Departures
- Filter by destination: London St Pancras
- Provider: Eurostar

#### Train Number Mode
Look up a specific train:

1. Switch to "Train Number" mode
2. Enter the train number (e.g., "6611")
3. Select travel date
4. Optionally filter by provider

### Available Stations & Routes

**French Domestic:**
- Paris Montparnasse ↔ Bordeaux
- Paris Gare de Lyon ↔ Aix-en-Provence TGV
- Paris Gare de Lyon ↔ Lyon Part-Dieu
- Paris Gare l'Est ↔ Metz
- Aix-en-Provence TGV ↔ Lyon Part-Dieu

**International:**
- Paris Gare du Nord ↔ London St Pancras (Eurostar) 🇬🇧

### Supported Operators

- **TGV INOUI** - Standard SNCF high-speed service
- **OUIGO** - Low-cost SNCF high-speed trains
- **TGV Lyria** - France-Switzerland routes (Paris/Lyon to Geneva, Lausanne, Zurich, Basel)
- **Eurostar** - France-UK routes (Paris to London)
- **DB SNCF** - Germany-France routes
- **Trenitalia** - Italian high-speed (routes TBD)
- **Renfe** - Spanish high-speed (routes TBD)

## Development

### Project Structure

```
tgvtimes/
├── src/
│   ├── backend/          # API client layer
│   │   └── sncf_api.py   # Navitia API integration
│   ├── config/           # Configuration
│   │   └── logger.py     # Centralized logging
│   ├── data/             # Data files and scripts
│   │   ├── scripts/      # Utility scripts
│   │   └── stations.json # Station configurations
│   └── frontend/         # Streamlit UI
│       ├── app.py        # Main application
│       └── utils.py      # Helper functions
├── Makefile              # Development commands
├── pyproject.toml        # Project dependencies
└── README.md
```

### Development Commands

```bash
# Run linting checks
make lint

# Auto-fix linting issues
make lint-fix

# Format code
make format

# Clean cache files
make clean
```

### Adding New Stations

Edit `src/data/stations.json` or run the station fetcher script:

```bash
uv run python src/data/scripts/fetch_station_ids.py
```

## Deployment

### Deploy to Streamlit Cloud (Free)

1. **Fork or push to GitHub** (already done!)

2. **Go to [Streamlit Cloud](https://share.streamlit.io/)**

3. **Sign in** with your GitHub account

4. **Click "New app"**

5. **Configure your app**:
   - Repository: `Gauthierkk/tgvtimes`
   - Branch: `main`
   - Main file path: `src/frontend/app.py`

6. **Add your API key**:
   - Click "Advanced settings"
   - Go to "Secrets" section
   - Add your secret in TOML format:

   ```toml
   SNCF_API_KEY = "your_api_key_here"
   ```

7. **Click "Deploy"**

Your app will be live at `https://[your-app-name].streamlit.app`!

### Environment Variables for Deployment

When deploying to Streamlit Cloud, configure secrets in the dashboard:

```toml
# .streamlit/secrets.toml (for Streamlit Cloud)
SNCF_API_KEY = "your_api_key_here"
```

The app automatically reads from both `.env` (local) and Streamlit secrets (cloud).

## Logging

The application uses structured logging with timestamps, log levels, module names, and function names:

```
2025-10-10 16:42:08 | INFO     | __main__                       | main                 | Starting TGV Times Dashboard
2025-10-10 16:42:08 | DEBUG    | backend.sncf_api               | get_journeys         | Fetching journeys from...
```

Logs are written to:
- **Console**: INFO level and above
- **File**: `tgvtimes.log` (all levels including DEBUG)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [SNCF Navitia API](https://www.navitia.io/) for providing train schedule data
- [Streamlit](https://streamlit.io/) for the amazing web framework
- [uv](https://github.com/astral-sh/uv) for fast package management

## Troubleshooting

### API Key Issues

If you see "API key not configured":
- Check that `.env` file exists in project root
- Verify the key format: `SNCF_API_KEY=your_key` (no quotes needed)
- Restart the Streamlit app after adding the key

### Station Not Found

If a station isn't found:
- Check `src/data/stations.json` for available stations
- Use the fetch script to add new stations
- Ensure the station name matches exactly

### Connection Errors

If you get connection errors:
- Check your internet connection
- Verify API key is valid at [navitia.io](https://www.navitia.io/)
- Check API rate limits (free tier has limits)

## Support

For issues and questions:
- Open an [issue](https://github.com/Gauthierkk/tgvtimes/issues)
- Check existing issues for solutions

---

Made with ❤️ using Claude Code
