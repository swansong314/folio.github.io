document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('portfolioForm');
    const submitBtn = document.getElementById('submitBtn');
    const loading = document.getElementById('loading');
    const message = document.getElementById('message');
    
    // Replace this URL with your actual API Gateway endpoint after deployment
    const API_ENDPOINT = 'https://psyqys4qb7.execute-api.us-east-1.amazonaws.com/prod/create';
    
    // Initialize dynamic form functionality
    initializeDynamicForms();
    
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
        
        // Collect enhanced form data
        const formData = collectFormData();
        formData.captcha_token = captchaResponse;
        
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
    
    function collectFormData() {
        const data = {
            // Personal Information
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            altEmail: document.getElementById('altEmail').value,
            phone1: document.getElementById('phone1').value,
            phone2: document.getElementById('phone2').value,
            bio: document.getElementById('bio').value,
            github_pat: document.getElementById('github_pat').value,
            
            // Professional Links
            links: collectArrayData('linkType[]', 'linkUrl[]'),
            
            // Projects
            projects: collectComplexArrayData([
                'projectTitle[]',
                'projectDescription[]', 
                'projectTechnologies[]',
                'projectLink[]'
            ], ['title', 'description', 'technologies', 'link']),
            
            // Experience  
            experience: collectComplexArrayData([
                'experienceTitle[]',
                'experienceCompany[]',
                'experienceDuration[]',
                'experienceDescription[]'
            ], ['title', 'company', 'duration', 'description']),
            
            // Education
            education: collectComplexArrayData([
                'educationType[]',
                'educationQualification[]',
                'educationInstitution[]',
                'educationYear[]'
            ], ['type', 'qualification', 'institution', 'year']),
            
            // Achievements
            achievements: collectComplexArrayData([
                'achievementTitle[]',
                'achievementDescription[]'
            ], ['title', 'description'])
        };
        
        return data;
    }
    
    function collectArrayData(typeSelector, urlSelector) {
        const types = document.querySelectorAll(`[name="${typeSelector}"]`);
        const urls = document.querySelectorAll(`[name="${urlSelector}"]`);
        const result = [];
        
        for (let i = 0; i < types.length; i++) {
            if (types[i].value && urls[i].value) {
                result.push({
                    type: types[i].value,
                    url: urls[i].value
                });
            }
        }
        
        return result;
    }
    
    function collectComplexArrayData(selectors, keys) {
        const elements = selectors.map(selector => 
            document.querySelectorAll(`[name="${selector}"]`)
        );
        
        const result = [];
        const length = elements[0].length;
        
        for (let i = 0; i < length; i++) {
            const item = {};
            let hasContent = false;
            
            elements.forEach((elementList, index) => {
                const value = elementList[i]?.value || '';
                item[keys[index]] = value;
                if (value) hasContent = true;
            });
            
            if (hasContent) {
                result.push(item);
            }
        }
        
        return result;
    }
    
    function initializeDynamicForms() {
        // Professional Links
        setupDynamicSection('addLink', 'linksContainer', createLinkItem, '.remove-link');
        
        // Projects
        setupDynamicSection('addProject', 'projectsContainer', createProjectItem, '.remove-project');
        
        // Experience
        setupDynamicSection('addExperience', 'experienceContainer', createExperienceItem, '.remove-experience');
        
        // Education
        setupDynamicSection('addEducation', 'educationContainer', createEducationItem, '.remove-education');
        
        // Achievements
        setupDynamicSection('addAchievement', 'achievementsContainer', createAchievementItem, '.remove-achievement');
    }
    
    function setupDynamicSection(addButtonId, containerId, createItemFunction, removeSelector) {
        const addButton = document.getElementById(addButtonId);
        const container = document.getElementById(containerId);
        
        addButton.addEventListener('click', function() {
            const newItem = createItemFunction();
            container.appendChild(newItem);
            
            // Add remove functionality to the new item
            const removeButton = newItem.querySelector(removeSelector);
            if (removeButton) {
                removeButton.addEventListener('click', function() {
                    newItem.remove();
                });
            }
        });
        
        // Add remove functionality to existing items
        container.addEventListener('click', function(e) {
            if (e.target.matches(removeSelector)) {
                e.target.closest('.link-item, .project-item, .experience-item, .education-item, .achievement-item').remove();
            }
        });
    }
    
    function createLinkItem() {
        const div = document.createElement('div');
        div.className = 'link-item';
        div.innerHTML = `
            <select name="linkType[]" class="link-type">
                <option value="github">GitHub</option>
                <option value="linkedin">LinkedIn</option>
                <option value="leetcode">LeetCode</option>
                <option value="portfolio">Portfolio</option>
                <option value="other">Other</option>
            </select>
            <input type="url" name="linkUrl[]" placeholder="https://github.com/username" class="link-url">
            <button type="button" class="remove-link">Remove</button>
        `;
        return div;
    }
    
    function createProjectItem() {
        const div = document.createElement('div');
        div.className = 'project-item';
        div.innerHTML = `
            <div class="form-group">
                <label>Project Title *</label>
                <input type="text" name="projectTitle[]" required placeholder="My Awesome Project">
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea name="projectDescription[]" placeholder="Brief description of the project..."></textarea>
            </div>
            <div class="form-group">
                <label>Technologies Used</label>
                <input type="text" name="projectTechnologies[]" placeholder="JavaScript, React, Node.js">
            </div>
            <div class="form-group">
                <label>Project Links</label>
                <input type="url" name="projectLink[]" placeholder="https://github.com/username/project">
            </div>
            <button type="button" class="remove-project">Remove Project</button>
        `;
        return div;
    }
    
    function createExperienceItem() {
        const div = document.createElement('div');
        div.className = 'experience-item';
        div.innerHTML = `
            <div class="form-group">
                <label>Job Title *</label>
                <input type="text" name="experienceTitle[]" required placeholder="Software Engineer">
            </div>
            <div class="form-group">
                <label>Company *</label>
                <input type="text" name="experienceCompany[]" required placeholder="Tech Corp Inc.">
            </div>
            <div class="form-group">
                <label>Duration</label>
                <input type="text" name="experienceDuration[]" placeholder="Jan 2020 - Present">
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea name="experienceDescription[]" placeholder="Key responsibilities and achievements..."></textarea>
            </div>
            <button type="button" class="remove-experience">Remove Experience</button>
        `;
        return div;
    }
    
    function createEducationItem() {
        const div = document.createElement('div');
        div.className = 'education-item';
        div.innerHTML = `
            <div class="form-group">
                <label>Education Type *</label>
                <select name="educationType[]" required>
                    <option value="">Select Type</option>
                    <option value="bachelors">Bachelor's Degree</option>
                    <option value="masters">Master's Degree</option>
                    <option value="phd">Ph.D.</option>
                    <option value="diploma">Diploma</option>
                    <option value="certificate">Certificate</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <div class="form-group">
                <label>Qualification *</label>
                <input type="text" name="educationQualification[]" required placeholder="B.Tech Computer Science">
            </div>
            <div class="form-group">
                <label>Institution *</label>
                <input type="text" name="educationInstitution[]" required placeholder="University of Technology">
            </div>
            <div class="form-group">
                <label>Year/Duration</label>
                <input type="text" name="educationYear[]" placeholder="2018-2022">
            </div>
            <button type="button" class="remove-education">Remove Education</button>
        `;
        return div;
    }
    
    function createAchievementItem() {
        const div = document.createElement('div');
        div.className = 'achievement-item';
        div.innerHTML = `
            <div class="form-group">
                <label>Achievement Title *</label>
                <input type="text" name="achievementTitle[]" required placeholder="Winner of Hackathon 2023">
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea name="achievementDescription[]" placeholder="Details about the achievement..."></textarea>
            </div>
            <button type="button" class="remove-achievement">Remove Achievement</button>
        `;
        return div;
    }
    
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