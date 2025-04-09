document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const pdfFileInput = document.getElementById('pdfFile');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const uploadBtn = document.getElementById('uploadBtn');
    const loadingContainer = document.getElementById('loadingContainer');
    const loadingMessage = document.getElementById('loadingMessage');
    const waitTimeElement = document.getElementById('waitTime');
    const errorContainer = document.getElementById('errorContainer');
    const errorMessage = document.getElementById('errorMessage');
    const retryBtn = document.getElementById('retryBtn');
    const resultsContainer = document.getElementById('resultsContainer');
    const summaryContent = document.getElementById('summaryContent');
    const newSummaryBtn = document.getElementById('newSummaryBtn');

    // Variables
    let waitTimeCounter = 0;
    let waitTimeInterval;
    let selectedFile = null;
    const MAX_WAIT_TIME = 5 * 60; // 5 minutes in seconds
    const API_ENDPOINT = 'http://127.0.0.1:8000/upload-pdf/';

    // File selection event
    pdfFileInput.addEventListener('change', function(event) {
        selectedFile = event.target.files[0];
        
        if (selectedFile) {
            // Display file name
            fileName.textContent = selectedFile.name;
            fileInfo.classList.remove('d-none');
            // Enable upload button
            uploadBtn.disabled = false;
        } else {
            fileInfo.classList.add('d-none');
            uploadBtn.disabled = true;
        }
    });

    // Upload and Summarize button click
    uploadBtn.addEventListener('click', function() {
        if (!selectedFile) {
            showError('Please select a PDF file first.');
            return;
        }
        
        // Show loading indicator and hide other containers
        loadingContainer.classList.remove('d-none');
        errorContainer.classList.add('d-none');
        resultsContainer.classList.add('d-none');
        uploadBtn.disabled = true;
        pdfFileInput.disabled = true;
        
        // Start the wait time counter
        waitTimeCounter = 0;
        waitTimeElement.textContent = waitTimeCounter;
        clearInterval(waitTimeInterval);
        waitTimeInterval = setInterval(updateWaitTime, 1000);
        
        // Prepare form data
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        // Make the API request
        fetch(API_ENDPOINT, {
            method: 'POST',
            body: formData,
            // No need to set Content-Type header as it's automatically set for FormData
        })
        .then(response => {
            clearInterval(waitTimeInterval);
            
            if (!response.ok) {
                // Handle HTTP errors
                return response.text().then(text => {
                    throw new Error(`HTTP error ${response.status}: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            // Hide loading indicator
            loadingContainer.classList.add('d-none');
            
            // Check if summary exists in the response
            if (data && data.Summary) {
                // Display the summary
                summaryContent.textContent = data.Summary;
                resultsContainer.classList.remove('d-none');
            } else {
                throw new Error('No summary found in the response.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loadingContainer.classList.add('d-none');
            showError(error.message || 'An error occurred while processing your request.');
        })
        .finally(() => {
            pdfFileInput.disabled = false;
        });
    });

    // Update wait time counter
    function updateWaitTime() {
        waitTimeCounter++;
        waitTimeElement.textContent = waitTimeCounter;
        
        // Update message based on wait time
        if (waitTimeCounter > 30 && waitTimeCounter <= 60) {
            loadingMessage.textContent = "Still processing... PDF analysis takes time";
        } else if (waitTimeCounter > 60 && waitTimeCounter <= 120) {
            loadingMessage.textContent = "Almost there... AI is generating your summary";
        } else if (waitTimeCounter > 120) {
            loadingMessage.textContent = "Thank you for your patience... Complex PDFs take longer to process";
        }
        
        // Check if we've reached the maximum wait time
        if (waitTimeCounter >= MAX_WAIT_TIME) {
            clearInterval(waitTimeInterval);
            showError('Request timed out after 5 minutes. Please try again.');
            loadingContainer.classList.add('d-none');
        }
    }

    // Show error message
    function showError(message) {
        errorMessage.textContent = message;
        errorContainer.classList.remove('d-none');
    }

    // Retry button click
    retryBtn.addEventListener('click', function() {
        errorContainer.classList.add('d-none');
        uploadBtn.disabled = false;
        // Allow the user to try again with the same file
    });

    // New Summary button click
    newSummaryBtn.addEventListener('click', function() {
        // Reset the form
        pdfFileInput.value = '';
        fileInfo.classList.add('d-none');
        resultsContainer.classList.add('d-none');
        uploadBtn.disabled = true;
        selectedFile = null;
    });
});
