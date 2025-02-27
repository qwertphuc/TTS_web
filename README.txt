README

This project requires the following steps to set up and run:

1. **Install Dependencies**:
   - Ensure you have Python installed on your system.
   - Download and install the required dependencies by running:
     ```
     pip install -r requirements.txt
     ```

2. **Run the Application Locally**:
   - To test the application locally, run the following command:
     ```
     python app.py
     ```
   - This will start the application on your local machine for testing purposes.

***IMPORTANT***  Install FFmpeg Add FFmpeg to your PATH


3. **Create a Docker Image**:
   - To containerize the application, build a Docker image using the provided Dockerfile:
     ```
     docker build -t your-image-name .
     ```
   - Replace `your-image-name` with a suitable name for your Docker image.

4. **Run the Application in Docker**:
   - After building the Docker image, run the application in a Docker container:
     ```
     docker run -p 5000:5000 your-image-name
     ```
   - This will start the application inside a Docker container and map port 5000 on your local machine to port 5000 in the container.

5. **Access the Application**:
   - Once the application is running (either locally or in Docker), you can access it by navigating to `http://localhost:5000` in your web browser.

---

For any issues or further assistance, please refer to the project documentation or contact the maintainer.