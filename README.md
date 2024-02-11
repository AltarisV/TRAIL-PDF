# TRAIL

A PDF to Alt-Text Generator.

## Description
TRAIL is a web application that converts PDF files into images, sends them to the GPT-4 Vision Model, and generates alternative text for each image. The resulting text is provided as a downloadable HTML file, enhanced with tags for screen reader accessibility.
By utilizing the GPT-4 Vision Model, mathematical formulas found in the source document will be converted into raw LaTeX-code in the resulting HTML, which allows screen readers to parse them.

### Speed and estimated Costs
Currently, generating alternative text for a pdf will take at least 6 seconds per page.
As a rough estimation, the API cost of generating alternative text via TRAIL is about 1.5 cents per page.

## Getting Started

### Prerequisites
Before you begin, ensure you have met the following requirements:
- You have an OpenAI-API Key and are at least Tier 1 (meaning you have charged at least 5$ of credit).
- You have installed the latest version of [Docker](https://www.docker.com/products/docker-desktop).
- You have a Windows/Linux/Mac machine capable of running Docker.

### Installing TRAIL

To install TRAIL, follow these steps:

#### Clone the repository:

```bash
git clone https://github.com/yourusername/yourrepository.git
cd yourrepository
```

#### Configuring the Application

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

- Bundling the Application for ease of use
- Testing and refining Code Markdown to HTML
- Giving a Side-by-Side of the PDF pages and corresponding HTML for easy post-editing

## Contributing to TRAIL

To contribute to TRAIL, follow these steps:

1. Fork this repository.
2. Create a new branch (`git checkout -b feature_branch`).
3. Make changes and test.
4. Commit your changes (`git commit -am 'Add some feature'`).
5. Push to the branch (`git push origin feature_branch`).
6. Create a new Pull Request.
