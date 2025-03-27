# TRAIL

A PDF to accessible HTML-Script Generator. Check out the latest release here: [Latest Release](https://github.com/AltarisV/TRAIL-PDF/releases)

## Description
TRAIL is a web application that converts PDF files into images, sends them to the GPT-4o Model, and generates alternative text for each image. 
The resulting text is then downloaded as an HTML file, which enables a blind person to navigate them with a screenreader. 
By utilizing GPT-4o, TRAIL is able to turn non-accessible PDF contents into neatly structured HTML files that include 
image descriptions for important images, HTML tables, structured Code and descriptions of mathematical
formulas.

## Getting Started

### Prerequisites
Before you begin, ensure you have an [OpenAI API Key](https://openai.com/blog/openai-api) and are at least Tier 1 (meaning you have charged at least $5 of credit).

### Using the latest TRAIL release
To use TRAIL using the bundled release, simply unpack the folder and start TRAIL.exe.
On first startup, you will be asked to input your OpenAI API Key, which will be saved in a separate file.
Afterwards, your browser will open a new Tab where you can use TRAIL.

### Speed and Estimated Costs
Currently, generating alternative text for a PDF will take around 5-8 seconds per page, depending on the amount of information on it.
As a rough estimation, the API cost of generating alternative text via TRAIL is approximately 1 cent per page.

## Working on TRAIL

Before working on TRAIL, make sure you have have installed the latest version of Docker or [Docker Desktop](https://www.docker.com/products/docker-desktop).
To start working on TRAIL, follow these steps:

### Configuring the Application

Create a `.env` file in the project root directory and add the following configurations:

```env
OPENAI_API_KEY='your_openai_api_key_here'
APP_SECRET_KEY='your_secret_key_here'
```

### Running TRAIL

To run TRAIL, execute the following command in the root directory of the project:

```bash
docker-compose up
```

This will build and start the TRAIL application in a Docker container. You can access the web application by navigating to `http://localhost:7777` in your web browser.

## Planned

- Showing the current progress for PDF-conversion
- Giving a Side-by-Side of the PDF pages and corresponding HTML for easy post-editing 
