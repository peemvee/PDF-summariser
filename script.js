document.addEventListener('DOMContentLoaded', function() {
    const pdfFileInput   = document.getElementById('pdfFile');
    const fileInfo       = document.getElementById('fileInfo');
    const fileName       = document.getElementById('fileName');
    const uploadBtn      = document.getElementById('uploadBtn');
    const loadingContainer = document.getElementById('loadingContainer');
    const loadingMessage   = document.getElementById('loadingMessage');
    const waitTimeElement  = document.getElementById('waitTime');
    const errorContainer   = document.getElementById('errorContainer');
    const errorMessage     = document.getElementById('errorMessage');
    const retryBtn         = document.getElementById('retryBtn');
    const resultsContainer = document.getElementById('resultsContainer');
    const summaryContent   = document.getElementById('summaryContent');
    const newSummaryBtn    = document.getElementById('newSummaryBtn');
  
    const optionsContainer = document.getElementById('optionsContainer');
    const wordLimitInput   = document.getElementById('wordLimit');
    const wordLimitValue   = document.getElementById('wordLimitValue');
    const toneSelect       = document.getElementById('toneSelect');
  
    let waitTimeCounter = 0;
    let waitTimeInterval;
    let selectedFile = null;
    const MAX_WAIT_TIME = 5 * 60;
    const API_ENDPOINT  = 'http://127.0.0.1:8000/upload-pdf/';
  
    pdfFileInput.addEventListener('change', function(e) {
      selectedFile = e.target.files[0];
      if (selectedFile) {
        fileName.textContent = selectedFile.name;
        fileInfo.classList.remove('d-none');
        optionsContainer.classList.remove('d-none');
        uploadBtn.disabled = false;
      } else {
        fileInfo.classList.add('d-none');
        optionsContainer.classList.add('d-none');
        uploadBtn.disabled = true;
      }
    });
  
    wordLimitInput.addEventListener('input', () => {
      wordLimitValue.textContent = wordLimitInput.value;
    });
  
    uploadBtn.addEventListener('click', function() {
      if (!selectedFile) return showError('Please select a PDF first.');
  
      loadingContainer.classList.remove('d-none');
      errorContainer.classList.add('d-none');
      resultsContainer.classList.add('d-none');
      uploadBtn.disabled = true;
      pdfFileInput.disabled = true;
  
      waitTimeCounter = 0;
      waitTimeElement.textContent = 0;
      clearInterval(waitTimeInterval);
      waitTimeInterval = setInterval(updateWaitTime, 1000);
  
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('word_limit', wordLimitInput.value);
      formData.append('tone', toneSelect.value);
  
      fetch(API_ENDPOINT, {
        method: 'POST',
        body: formData
      })
      .then(async res => {
        clearInterval(waitTimeInterval);
        if (!res.ok) {
          const t = await res.text();
          throw new Error(`HTTP ${res.status}: ${t}`);
        }
        return res.json();
      })
      .then(data => {
        loadingContainer.classList.add('d-none');
        if (data.Summary) {
          summaryContent.textContent = data.Summary;
          resultsContainer.classList.remove('d-none');
        } else {
          throw new Error('No summary in response.');
        }
      })
      .catch(err => {
        console.error(err);
        loadingContainer.classList.add('d-none');
        showError(err.message || 'Error processing request.');
      })
      .finally(() => {
        pdfFileInput.disabled = false;
      });
    });
  
    function updateWaitTime() {
      waitTimeCounter++;
      waitTimeElement.textContent = waitTimeCounter;
      if (waitTimeCounter > 30 && waitTimeCounter <= 60) {
        loadingMessage.textContent = "Still processing... PDF analysis takes time";
      } else if (waitTimeCounter > 60 && waitTimeCounter <= 120) {
        loadingMessage.textContent = "Almost there... AI is generating your summary";
      } else if (waitTimeCounter > 120) {
        loadingMessage.textContent = "Thanks for your patience...";
      }
      if (waitTimeCounter >= MAX_WAIT_TIME) {
        clearInterval(waitTimeInterval);
        showError('Timed out after 5 minutes. Please try again.');
        loadingContainer.classList.add('d-none');
      }
    }
  
    function showError(msg) {
      errorMessage.textContent = msg;
      errorContainer.classList.remove('d-none');
    }
  
    retryBtn.addEventListener('click', () => {
      errorContainer.classList.add('d-none');
      uploadBtn.disabled = false;
    });
  
    newSummaryBtn.addEventListener('click', () => {
      pdfFileInput.value = '';
      fileInfo.classList.add('d-none');
      optionsContainer.classList.add('d-none');
      resultsContainer.classList.add('d-none');
      uploadBtn.disabled = true;
      selectedFile = null;
    });
  });
  