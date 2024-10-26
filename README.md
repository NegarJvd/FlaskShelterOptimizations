# Shelter Design Optimizer

This project provides a suite of tools and optimizations for designing shelter cross-sections, calculating joint details, and assessing load capacity. Additionally, it includes an API to verify design status under various conditions and a G-code generator for CNC machining specific designs. The API also offers an interactive Swagger documentation interface for testing and exploring endpoints.

## Features
- **Cross-Section & Joint Optimizations**: Optimize the structural design of shelter components.
- **Load Calculator**: Calculate loads and verify safety for various shelter configurations.
- **Design Verification API**: Validate design status for different scenarios and structural requirements.
- **G-code Generator**: Automatically generates CNC-compatible G-code for specified designs.

## Getting Started

### Prerequisites
- **Python** and **Flask** installed on your system.
- **Swagger** is configured for API documentation.

### Running the Project
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd shelter-design-optimizer

2. **Set Up a Virtual Environment:**
    - Create a virtual environment:
        ```bash
        python3 -m venv venv
    - Activate the virtual environment:
        - On Windows:
            ```bash
            .venv\Scripts\activate

        - On macOS/Linux:
            ```bash
            source venv/bin/activate

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt

4. **Update Configuration:**
    Edit **app.py** to replace **flask.locknl.com** with your domain name to ensure Swagger and other domain-dependent configurations work.

5. **Run the Flask Application**:  
    ```bash
    python  app.py
    
6. **Access Swagger Documentation:**
    - After running, open your browser and go to:
        ```arduino
        http://your-domain.com/swagger.json
    - Replace **your-domain.com** with the actual domain or **localhost** if testing locally.

This project is now ready for you to explore various shelter optimizations and generate CNC G-code directly from your verified designs. Enjoy building safe, efficient shelter structures!
