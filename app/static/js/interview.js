document.addEventListener('DOMContentLoaded', function() {
    // Auto-resize textareas based on content
    const textareas = document.querySelectorAll('textarea[data-min-rows]');
    
    function autoResizeTextarea(textarea) {
        const minRows = parseInt(textarea.getAttribute('data-min-rows')) || 6;
        const maxRows = parseInt(textarea.getAttribute('data-max-rows')) || 20;
        
        function resize() {
            // Reset height to auto to get the correct scrollHeight
            textarea.style.height = 'auto';
            
            // Calculate the height based on scrollHeight
            const contentHeight = textarea.scrollHeight;
            const lineHeight = parseInt(window.getComputedStyle(textarea).lineHeight);
            const rows = Math.floor(contentHeight / lineHeight);
            
            // Constrain the number of rows
            const newRows = Math.min(Math.max(rows, minRows), maxRows);
            textarea.rows = newRows;
            
            // Set the height to auto to allow shrinking
            textarea.style.height = 'auto';
            textarea.style.overflowY = newRows >= maxRows ? 'auto' : 'hidden';
        }
        
        // Initial resize
        resize();
        
        // Add event listeners
        textarea.addEventListener('input', resize);
        window.addEventListener('resize', resize);
    }
    
    // Apply auto-resize to all matching textareas
    textareas.forEach(autoResizeTextarea);
    
    // Handle form submission for answer evaluation
    const interviewForm = document.getElementById('interview-form');
    if (interviewForm) {
        interviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Evaluating...';
            
            // Collect form data
            const formData = new FormData(this);
            
            // Add CSRF token
            const csrfToken = document.querySelector('input[name="csrf_token"]').value;
            
            // Send the data to the server
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    // Handle HTTP errors (like 500, 503, etc.)
                    return response.json().catch(() => {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }).then(errData => {
                        // If we got JSON with an error message, use it
                        if (errData && errData.error) {
                            throw new Error(errData.error);
                        }
                        throw new Error(`Server responded with status: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Process successful evaluation
                    const evaluations = data.evaluations;
                    const questionBlocks = document.querySelectorAll('.question-block');
                    
                    evaluations.forEach((evaluation, index) => {
                        if (questionBlocks[index]) {
                            const feedbackDiv = questionBlocks[index].querySelector('.answer-feedback');
                            const alertDiv = feedbackDiv.querySelector('.alert');
                            const correctAnswerDiv = feedbackDiv.querySelector('.correct-answer');
                            
                            // Clear previous feedback safely
                            if (alertDiv) {
                                alertDiv.className = 'alert';
                                alertDiv.innerHTML = '';
                            }
                            if (correctAnswerDiv) {
                                correctAnswerDiv.innerHTML = '';
                            }
                            
                            // Set alert class based on verdict
                            const alertClass = evaluation.verdict === 'Correct' ? 'alert-success' : 
                                            evaluation.verdict === 'Incomplete' ? 'alert-warning' : 'alert-danger';
                            
                            // Safely update alert div if it exists
                            if (alertDiv) {
                                // Clear existing classes and add new ones
                                alertDiv.className = 'alert';
                                alertDiv.classList.add(alertClass);
                                alertDiv.innerHTML = `
                                    <strong>${evaluation.verdict}!</strong> ${evaluation.explanation || 'No feedback available.'}
                                `;
                            }
                            
                            // Show correct answer if answer was incorrect
                            if ((evaluation.verdict === 'Incorrect' || evaluation.verdict === 'Error') && evaluation.model_answer) {
                                correctAnswerDiv.innerHTML = `
                                    <div class="card border-info mt-2">
                                        <div class="card-header bg-info text-white">
                                            <strong>Model Answer:</strong>
                                        </div>
                                        <div class="card-body p-3">
                                            <p class="card-text mb-0">${evaluation.model_answer}</p>
                                        </div>
                                    </div>
                                `;
                            }
                            
                            // Show the feedback
                            feedbackDiv.classList.remove('d-none');
                        }
                    });
                    
                    // Scroll to first question
                    if (questionBlocks.length > 0) {
                        questionBlocks[0].scrollIntoView({ behavior: 'smooth' });
                    }
                    
                    // Show success message
                    const successAlert = `
                        <div class="alert alert-success alert-dismissible fade show" role="alert">
                            <i class="bi bi-check-circle-fill me-2"></i>
                            Your answers have been evaluated successfully!
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    `;
                    document.querySelector('#questions-container').insertAdjacentHTML('afterbegin', successAlert);
                    
                } else {
                    // Show error message from server
                    throw new Error(data.error || 'An unknown error occurred while evaluating your answers.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Check if this is an AI service error
                let errorMessage = 'An unexpected error occurred. Please try again later.';
                
                if (error.message.includes('AI service') || 
                    error.message.includes('unavailable') ||
                    error.message.includes('503') ||
                    error.message.includes('internal error occurred')) {
                    errorMessage = `
                        <div>
                            <p>The AI evaluation service is currently experiencing high demand or is temporarily unavailable.</p>
                            <p class="mb-0">Please try again in a few minutes. If the problem persists, you can:</p>
                            <ul class="mb-0 mt-2">
                                <li>Try again after a short break</li>
                                <li>Check back later when the service might be less busy</li>
                                <li>Contact support if the issue continues</li>
                            </ul>
                        </div>
                    `;
                } else if (error.message) {
                    errorMessage = error.message;
                }
                
                const errorAlert = `
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>
                        ${errorMessage}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `;
                
                // Remove any existing alerts
                const existingAlerts = document.querySelectorAll('.alert.alert-danger.alert-dismissible');
                existingAlerts.forEach(alert => alert.remove());
                
                // Add new alert
                document.querySelector('#questions-container').insertAdjacentHTML('afterbegin', errorAlert);
                
                // Scroll to top to see the error message
                window.scrollTo({ top: 0, behavior: 'smooth' });
            })
            .finally(() => {
                // Re-enable the submit button
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
                
                // Re-initialize any dynamic elements
                const textareas = document.querySelectorAll('textarea[data-min-rows]');
                textareas.forEach(autoResizeTextarea);
            });
        });
    }
    
    // Handle the generate questions form
    const generateForm = document.querySelector('form[action*="interview-simulator"]');
    if (generateForm) {
        generateForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Generating...';
            
            // The form will submit normally, but we've updated the button state
        });
    }
});
