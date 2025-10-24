# Build Instructions for Budget Application

## Prerequisites
Before building the budget application, ensure you have the following installed:
- Python 3.7 or higher
- pip (Python package installer)

## Installation Steps

1. **Clone the Repository**
   Clone the budget application repository to your local machine using the following command:
   ```
   git clone <repository-url>
   ```

2. **Navigate to the Project Directory**
   Change your working directory to the project folder:
   ```
   cd budget-app
   ```

3. **Install Dependencies**
   Install the required Python packages listed in `requirements.txt`:
   ```
   pip install -r requirements.txt
   ```

4. **Build the Application**
   To build the application, you can use a packaging tool like `setuptools`. Create a source distribution and a wheel by running:
   ```
   python setup.py sdist bdist_wheel
   ```

5. **Run the Application**
   After building, you can run the application using:
   ```
   python src/budget_app/main.py
   ```

## Packaging for Distribution
To package the application for distribution, you can create a zip file containing the necessary files:
1. Include the `src`, `assets`, and `packaging` directories.
2. Ensure that the `requirements.txt` and `LICENSE` files are included.
3. Compress the folder into a zip file.

## Additional Notes
- Make sure to test the application thoroughly before distributing it.
- Update the version number in `pyproject.toml` for each release.