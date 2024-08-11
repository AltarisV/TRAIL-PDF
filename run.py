import os
import csv
from flask import Flask, jsonify, current_app
from app import create_app


def save_usage_to_csv(usage_info, filename="token_usage.csv"):
    """
    Saves token usage information to a CSV file.

    :param usage_info: Dictionary containing token usage data.
    :type usage_info: dict
    :param filename: The name of the CSV file to save the data in, defaults to "token_usage.csv".
    :type filename: str, optional
    :returns: None
    """
    LOG_DIR = current_app.config['TOKEN_USAGE_DIR']
    os.makedirs(LOG_DIR, exist_ok=True)  # Create the directory if it doesn't exist

    filepath = os.path.join(LOG_DIR, filename)
    file_exists = os.path.isfile(filepath)
    try:
        with open(filepath, "a", newline='') as csvfile:
            fieldnames = ['prompt_tokens', 'completion_tokens', 'total_tokens']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()  # Write the header only if the file doesn't exist

            writer.writerow(usage_info)
    except Exception as e:
        current_app.logger.error(f"Failed to save usage data to {filepath}: {e}")
        raise


def handle_global_exception(e):
    """
    Handle exceptions by returning a JSON response or an HTML page based on the request.
    Logs the error and returns a formatted response.

    :param e: Exception instance.
    :returns: A JSON response or an HTML page with the error details.
    """
    current_app.logger.error(f"An error occurred: {str(e)}")

    if current_app.config.get('DEBUG'):
        # If in debug mode, provide detailed error information
        response = jsonify({
            "error": str(e),
            "message": "An internal error occurred.",
        })
        response.status_code = 500
        return response
    else:
        # For production, provide a generic error message
        response = jsonify({
            "error": "Internal Server Error",
            "message": "Something went wrong on our end.",
        })
        response.status_code = 500
        return response


def create_app_with_exception_handling():
    """
    Creates and configures the Flask application with comprehensive error handling.

    :returns: The configured Flask application instance.
    :rtype: Flask
    """
    flask_app = create_app()

    # Register the global error handler
    flask_app.register_error_handler(Exception, handle_global_exception)

    return flask_app


if __name__ == '__main__':
    # Initialize the app with exception handling
    app_instance = create_app_with_exception_handling()

    # Run the application
    app_instance.run(host='0.0.0.0', port=7777, debug=True)
