document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('portfolioForm');
    const submitBtn = document.getElementById('submitBtn');
    const loading = document.getElementById('loading');
    const message = document.getElementById('message');
    
    // Replace this URL with your actual API Gateway endpoint after deployment
    const API_ENDPOINT = 'https://YOUR_API_GATEWAY_URL/prod/create';
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Show loading state
        submitBtn.disabled = true;
        loading.style.display = 'block';
        message.style.display = 'none';
        
        // Get hCaptcha response
        const captchaResponse = hcaptcha.getResponse();
        if (!captchaResponse) {
            showMessage('error', 'Please complete the CAPTCHA verification.');
            submitBtn.disabled = false;
            loading.style.display = 'none';
            return;
        }
        
        // Collect form data
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            bio: document.getElementById('bio').value,
            projects: document.getElementById('projects').value,
            github_pat: document.getElementById('github_pat').value,
            captcha_token: captchaResponse
        };
        
        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showMessage('success', `
                    🎉 Success! Your portfolio has been created.<br>
                    <strong>Repository:</strong> <a href="${result.repository_url}" target="_blank">${result.repository_url}</a><br>
                    <strong>Website:</strong> <a href="${result.pages_url}" target="_blank">${result.pages_url}</a><br>
                    <small>Note: It may take a few minutes for your website to be available.</small>
                `);
                
                // Clear the form and reset CAPTCHA
                form.reset();
                hcaptcha.reset();
            } else {
                showMessage('error', `Error: ${result.error}`);
            }
        } catch (error) {
            showMessage('error', `Network error: ${error.message}. Please check if the API endpoint is correct.`);
        } finally {
            // Hide loading state
            submitBtn.disabled = false;
            loading.style.display = 'none';
        }
    });
    
    function showMessage(type, text) {
        message.className = `message ${type}`;
        message.innerHTML = text;
        message.style.display = 'block';
        
        // Scroll to message
        message.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    // Show warning about API endpoint if it's not configured
    if (API_ENDPOINT.includes('YOUR_API_GATEWAY_URL')) {
        setTimeout(() => {
            showMessage('error', '⚠️ Please configure the API_ENDPOINT in script.js with your actual API Gateway URL after deploying the backend.');
        }, 1000);
    }
});