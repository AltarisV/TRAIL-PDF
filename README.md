# VisionScribe
A PDF to Alt-Text Generator (WIP).

## Getting Started

### Prerequisites
Before you begin, ensure you have met the following requirements:
- You have installed the latest version of [Python](https://www.python.org/downloads/).
- You have a Windows/Linux/Mac machine capable of running Python 3.8+.
- You have installed [Git](https://git-scm.com/downloads).
- You have Poppler in PATH

### Installing VisionScribe

To install VisionScribe, follow these steps:

#### Clone the repository:

    git clone https://github.com/yourusername/yourrepository.git
    cd yourrepository
   
### Create a virtual environment and activate it:

#### On Windows:
    
    python -m venv venv
    venv\Scripts\activate

#### On macOS and Linux:

    python3 -m venv venv
    source venv/bin/activate

#### Install the required packages:

    pip install -r requirements.txt

### Configuring the Application

#### Create a .env file in the project root directory and add the following configurations:

    OPENAI_API_KEY='your_openai_api_key_here'
    POPPLER_PATH='path_to_your_poppler_bin_directory'
    APP_SECRET_KEY='your_secret_key_here'

## Running VisionScribe

To run VisionScribe, execute:

    flask run

This will start the Flask server, and you can access the web application by navigating to http://127.0.0.1:7777 in your web browser.


## Contributing to VisionScribe

To contribute to VisionScribe, follow these steps:

1. Fork this repository. 
2. Create a new branch (git checkout -b feature_branch). 
3. Make changes and test. 
4. Commit your changes (git commit -am 'Add some feature'). 
5. Push to the branch (git push origin feature_branch). 
6. Create a new Pull Request.
