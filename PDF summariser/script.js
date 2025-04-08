// Get references to the HTML elements
const uploadForm = document.getElementById('uploadForm');
const pdfFileInput = document.getElementById('pdfFile');
const responseArea = document.getElementById('responseArea');

// Add event listener for form submission
uploadForm.addEventListener('submit', async (event) => {
    // Prevent the default form submission behavior
    event.preventDefault();

    // Get the selected file
    const file = pdfFileInput.files[0];

    // --- Client-Side Validations ---
    // Check if a file was selected
    if (!file) {
        responseArea.innerHTML = '<p class="error">Please select a PDF file first.</p>';
        return;
    }

    // Check if the file *looks* like a PDF based on filename extension
    // This is a quick check, the server validates properly
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        responseArea.innerHTML = '<p class="error">Selected file does not have a .pdf extension.</p>';
        // Note: You might still allow the upload attempt if desired,
        // letting the server give the final verdict. But this provides faster feedback.
        return;
    }

    // Show a loading message
    responseArea.innerHTML = '<p>Uploading...</p>';

    // Create a FormData object to package the file
    const formData = new FormData();
    // Append the file. The key 'file' MUST match the FastAPI parameter name:
    // async def upload_pdf(file: UploadFile):
    formData.append('file', file);

    try {
        // Define the API endpoint URL (Default FastAPI address and port)
        // Make sure this matches where your FastAPI app is running!
        const apiUrl = 'http://127.0.0.1:8000/upload/';

        // Make the API request using fetch
        const response = await fetch(apiUrl, {
            method: 'POST',
            body: formData // FormData sets the correct Content-Type header
        });

        // Parse the JSON response from the API
        const result = await response.json();

        // Check if the API response indicates success (status code 200)
        // AND if the response contains 'filename' (FastAPI success case)
        if (response.ok && result.filename) {
            // Display the successful response
            responseArea.innerHTML = `
                <p class="success">Success!</p>
                <pre>Filename: ${result.filename}</pre>
            `;
        } else {
            // Handle API-level errors (like non-PDF error from FastAPI)
            // or network errors that didn't throw earlier but weren't ok.
            const errorMessage = result.error || `API Error: ${response.status} ${response.statusText}`;
            throw new Error(errorMessage);
        }

    } catch (error) {
        // Handle network errors or errors thrown from the response check
        console.error('Upload Error:', error);
        responseArea.innerHTML = `<p class="error">Upload failed: ${error.message}</p>`;
    } finally {
        // Optional: Clear the file input after upload attempt
         // uploadForm.reset();
    }
});