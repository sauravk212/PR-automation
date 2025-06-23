// Handle reviewer selection
const reviewerCheckboxes = document.querySelectorAll('.reviewer-checkbox');
const reviewerNamesSpan = document.getElementById('reviewer-names');

function updateSelectedReviewers() {
    const selectedReviewers = Array.from(reviewerCheckboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.dataset.name);
    
    reviewerNamesSpan.textContent = selectedReviewers.length > 0 
        ? selectedReviewers.join(', ') 
        : 'None';
}

function initializeReviewerSelection() {
    reviewerCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedReviewers);
    });
}

function showError(message, details = '') {
    const result = document.getElementById('result');
    let errorMessage = `<div class="error">
        <div class="error-main">${message}</div>`;
    
    if (details) {
        errorMessage += `<div class="error-details">${details}</div>`;
    }
    
    errorMessage += '</div>';
    result.innerHTML = errorMessage;
    
    // Scroll error into view
    result.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function showSuccess(message) {
    const result = document.getElementById('result');
    result.innerHTML = `<div class="success">${message}</div>`;
    result.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// Handle form submission
function initializeFormSubmission() {
    const form = document.getElementById('prForm');
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get selected reviewer UUIDs
        const selectedReviewerUuids = Array.from(reviewerCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        
        loading.style.display = 'flex';
        result.innerHTML = '';
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    input_text: document.getElementById('input_text').value,
                    reviewer_uuids: selectedReviewerUuids
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                // Handle error response
                let errorDetails = '';
                if (data.details) {
                    // Format Bitbucket API error details if available
                    const details = data.details.error || data.details;
                    errorDetails = typeof details === 'string' ? details : JSON.stringify(details, null, 2);
                }
                showError(data.error, errorDetails);
            } else {
                // Handle success
                const prLink = data.links?.html?.href;
                if (prLink) {
                    showSuccess(`
                        PR created successfully! 
                        <a href="${prLink}" target="_blank" class="pr-link">View PR</a>
                    `);
                } else {
                    showSuccess('PR created successfully!');
                }
                
                // Clear the form
                form.reset();
                updateSelectedReviewers();
            }
        } catch (error) {
            showError('Network error or server is not responding. Please try again.');
        } finally {
            loading.style.display = 'none';
        }
    });
}

// Initialize all functionality when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeReviewerSelection();
    initializeFormSubmission();
});

document.addEventListener('DOMContentLoaded', function() {
    const settingsForm = document.getElementById('settingsForm');
    const saveButton = document.getElementById('saveSettingsBtn');
    const buttonText = saveButton.querySelector('.button-text');
    const loader = saveButton.querySelector('.loader');

    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            // Disable the button and show loader
            saveButton.disabled = true;
            loader.style.display = 'inline-block';

            // The form will submit normally, and the page will refresh when complete
            // If you want to handle the submission with AJAX instead, you can add that logic here
        });
    }
}); 