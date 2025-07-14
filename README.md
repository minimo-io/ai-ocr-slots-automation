# AI-OCR-Slots

This project leverages **Playwright** and **EasyOCR** to automate interactions with slot games. It extracts real-time game data and integrates with local **Ollama** models for intelligent suggestions based on round outcomes.

### Features

- **Automated Slot Game Control:** Uses Puppeteer to interact with web-based slot machines, including taking screenshots.
- **Real-time Data Extraction:** Employs EasyOCR to read and interpret visual information (like game results, symbols, or scores) directly from the game screenshots.
- **AI-Powered Analysis:** Feeds extracted data into local Ollama models to generate insights or strategic suggestions.
- **Dynamic Decision Making:** Enables the project to react to game states and potentially adapt its actions based on AI analysis.

### Project Structure

This repository is organized into two main components:

- **`auto-gameplay-slots/`**: Contains the Node.js application responsible for browser automation with **Puppeteer**. Its primary role is to control the slot game, navigate the interface, and capture screenshots of the game state.
- **`ollama-ocr-slots/`**: Houses the Python application that uses **EasyOCR** for optical character recognition on the screenshots provided by `puppeteer-slots`, and integrates with **Ollama** for AI-driven analysis and suggestions.

### Technologies Used

- **Puppeteer & Playwright:** Headless Chrome Node.js library for browser automation.
- **EasyOCR:** Ready-to-use OCR (Optical Character Recognition) tool for extracting text from images.
- **Ollama:** Framework for running large language models (LLMs) locally.
- **Node.js:** JavaScript runtime for executing the `auto-slot-gameplay` part of the project.
- **Python:** Programming language used for the `ollama-ocr-slots` part.
- **Conda:** Environment management system for Python and other languages.
