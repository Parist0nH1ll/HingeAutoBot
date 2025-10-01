# HingeAutoBot

An AI-powered automation agent for the Hinge dating app that can automatically like, pass, or comment on profiles based on customizable matching criteria.

## Features

- **Automated Profile Analysis**: Uses OpenAI GPT-4 to analyze profile text and make intelligent matching decisions
- **AI Vision**: Detects UI elements using OpenAI's vision models for intelligent interaction
- **OCR Text Extraction**: Extracts profile information using Tesseract OCR
- **Customizable Criteria**: Set your own matching preferences and deal-breakers
- **Smart Interactions**: Automatically likes, passes, or comments on profiles
- **Docker Support**: Easy deployment with Docker containers
- **Comprehensive Logging**: Detailed logs for monitoring and debugging

## Requirements

### System Requirements
- Python 3.11+
- Android device with Hinge app installed
- ADB (Android Debug Bridge) installed
- Tesseract OCR engine
- OpenAI API key with GPT-4 Vision access

### Python Dependencies
- pure-python-adb
- pillow
- pytesseract
- python-dotenv
- openai
- requests
- selenium
- beautifulsoup4

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd HingeAutoBot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR
- **macOS**: `brew install tesseract`
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
- **Windows**: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

### 4. Get OpenAI API Key
- Sign up at [OpenAI](https://platform.openai.com/)
- Create an API key with GPT-4 Vision access
- Add billing information (required for vision models)

### 5. Setup Environment Variables
```bash
cp .env-template .env
# Edit .env with your OpenAI API key and device settings
```

### 6. Device Setup
1. Enable Developer Options on your Android device
2. Enable USB Debugging
3. Connect device via USB or set up wireless ADB
4. Authorize your computer for debugging

## Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional
DEVICE_IP=192.168.1.100
DEVICE_PORT=5555
BOT_DELAY=3
LOG_LEVEL=INFO
```

### Matching Criteria
Customize your matching preferences in `config.json`:

```json
{
  "matching_criteria": {
    "min_age": 21,
    "max_age": 35,
    "preferred_interests": [
      "technology", "travel", "fitness", "music", "art"
    ],
    "deal_breakers": [
      "smoking", "drugs", "excessive drinking"
    ],
    "personality_traits": [
      "intelligent", "funny", "adventurous", "kind"
    ]
  }
}
```

## Usage

### Running the Bot

#### Option 1: Direct Python Execution
```bash
python -m app.main
```

#### Option 2: Docker
```bash
# Build the container
docker build -t hinge-autobot -f docker/Dockerfile .

# Run the container
docker run -it --rm \
  -e OPENAI_API_KEY=your-api-key \
  -v $(pwd)/screenshots:/app/screenshots \
  -v $(pwd)/logs:/app/logs \
  hinge-autobot
```

#### Option 3: Docker Compose
```bash
# Set environment variables in .env file
docker-compose -f docker/docker-compose.yml up
```

### Device Connection

#### USB Connection
1. Connect your Android device via USB
2. Enable USB debugging
3. Run the bot - it will automatically detect the device

#### Wireless Connection
```bash
# On your device, enable wireless debugging
adb tcpip 5555

# Connect from your computer
adb connect 192.168.1.100:5555
```

## How It Works

1. **Screen Capture**: The bot captures screenshots of your device
2. **AI Vision Detection**: GPT-4 Vision identifies profile screens and UI elements
3. **Text Extraction**: OCR extracts profile text and information
4. **AI Analysis**: GPT-4 Vision analyzes the entire profile (images + text) against your criteria
5. **Decision Making**: The bot decides to like, pass, or comment
6. **Automated Interaction**: Executes the decision by tapping/swiping

## Bot Behavior

### Like Decision
- Profiles that match most of your criteria
- High compatibility scores
- Shared interests and values

### Pass Decision
- Profiles with deal-breakers
- Low compatibility scores
- Age outside your range

### Comment Decision
- Interesting profiles that need conversation starters
- Good potential but need more interaction
- Generates personalized, witty comments

## Customization

### AI Vision Configuration
The bot now uses AI vision instead of template matching, making it more robust and adaptable to UI changes. No manual template creation is needed.

### Modifying Matching Logic
Edit the `ProfileAnalyzer` class to customize how profiles are evaluated:

```python
def analyze_profile(self, profile_text: str) -> ProfileDecision:
    # Your custom logic here
    pass
```

### Adjusting Interaction Delays
Modify timing in `config.json`:

```json
{
  "bot_delay": 3,
  "tap_delay": 1.0,
  "swipe_delay": 2.0,
  "text_delay": 0.5
}
```

## Troubleshooting

### Common Issues

#### Device Not Found
- Ensure USB debugging is enabled
- Check ADB connection: `adb devices`
- Try reconnecting the device

#### OCR Not Working
- Verify Tesseract is installed: `tesseract --version`
- Check image quality and text clarity
- Adjust OCR confidence thresholds

#### AI Analysis Failing
- Verify OpenAI API key is correct
- Check API quota and billing
- Review network connectivity

#### AI Vision Issues
- Ensure OpenAI API key has GPT-4 Vision access
- Check API quota and billing
- Verify image quality and format

### Debug Mode
Run with debug logging:
```bash
LOG_LEVEL=DEBUG python -m app.main
```

### Manual Testing
Test individual components:
```python
from app.device_manager import DeviceManager
from app.ui_detector import UIDetector

# Test device connection
device = DeviceManager(config)
device.connect()

# Test UI detection
detector = UIDetector(config)
screenshot = device.capture_screenshot()
is_profile = detector.is_profile_screen(screenshot)
```

## Safety and Ethics

### Important Considerations
- Use responsibly and in accordance with Hinge's terms of service
- Don't abuse the automation - use reasonable delays
- Be respectful in automated comments
- Monitor the bot's behavior regularly

### Rate Limiting
The bot includes built-in delays to avoid being detected as automated:
- 3-second delay between profile evaluations
- 1-second delay between taps
- 2-second delay between swipes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes only. Use at your own risk and in accordance with applicable terms of service.

## Disclaimer

This tool is for educational and research purposes. Users are responsible for complying with Hinge's terms of service and applicable laws. The authors are not responsible for any misuse or consequences of using this tool.
