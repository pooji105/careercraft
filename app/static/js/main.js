// CareerCraft Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation enhancement
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Loading state for buttons
    document.querySelectorAll('.btn-loading').forEach(function(button) {
        button.addEventListener('click', function() {
            var originalText = this.innerHTML;
            this.innerHTML = '<span class="loading me-2"></span>Loading...';
            this.disabled = true;
            
            // Re-enable after 3 seconds (for demo purposes)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 3000);
        });
    });

    // Mobile menu enhancement
    var navbarToggler = document.querySelector('.navbar-toggler');
    var navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when clicking on a link
        var navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    navbarCollapse.classList.remove('show');
                }
            });
        });
    }

    // Theme toggle (if implemented later)
    var themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
        });
    }

    // Load saved theme
    var savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }

    // Resume Builder Step Navigation
    const steps = document.querySelectorAll('.resume-step');
    if (steps.length > 0) {
        let currentStep = 0;
        function showStep(index) {
            steps.forEach((step, i) => {
                step.classList.toggle('d-none', i !== index);
            });
        }
        document.querySelectorAll('.next-step').forEach(btn => {
            btn.addEventListener('click', function() {
                if (currentStep < steps.length - 1) {
                    currentStep++;
                    showStep(currentStep);
                }
            });
        });
        document.querySelectorAll('.prev-step').forEach(btn => {
            btn.addEventListener('click', function() {
                if (currentStep > 0) {
                    currentStep--;
                    showStep(currentStep);
                }
            });
        });
        showStep(currentStep);
    }

    // Add Education dynamic fields
    const educationList = document.getElementById('education-list');
    const addEducationBtn = document.getElementById('add-education');
    if (educationList && addEducationBtn) {
        function addEducationField() {
            const idx = educationList.children.length;
            const eduDiv = document.createElement('div');
            eduDiv.className = 'card mb-2 p-3';
            eduDiv.innerHTML = `
                <div class="mb-2"><input type="text" class="form-control" placeholder="Institution" name="edu_institution_${idx}" required></div>
                <div class="mb-2"><input type="text" class="form-control" placeholder="Degree" name="edu_degree_${idx}" required></div>
                <div class="mb-2"><input type="text" class="form-control" placeholder="Year" name="edu_year_${idx}"></div>
                <button type="button" class="btn btn-sm btn-danger remove-edu">Remove</button>
            `;
            educationList.appendChild(eduDiv);
            eduDiv.querySelector('.remove-edu').addEventListener('click', function() {
                eduDiv.remove();
            });
        }
        addEducationBtn.addEventListener('click', addEducationField);
    }

    // Add Experience dynamic fields
    const experienceList = document.getElementById('experience-list');
    const addExperienceBtn = document.getElementById('add-experience');
    if (experienceList && addExperienceBtn) {
        function addExperienceField() {
            const idx = experienceList.children.length;
            const expDiv = document.createElement('div');
            expDiv.className = 'card mb-2 p-3';
            expDiv.innerHTML = `
                <div class="mb-2"><input type="text" class="form-control" placeholder="Company" name="exp_company_${idx}" required></div>
                <div class="mb-2"><input type="text" class="form-control" placeholder="Role" name="exp_role_${idx}" required></div>
                <div class="mb-2"><input type="text" class="form-control" placeholder="Duration" name="exp_duration_${idx}"></div>
                <div class="mb-2"><textarea class="form-control" placeholder="Description" name="exp_desc_${idx}"></textarea></div>
                <button type="button" class="btn btn-sm btn-danger remove-exp">Remove</button>
            `;
            experienceList.appendChild(expDiv);
            expDiv.querySelector('.remove-exp').addEventListener('click', function() {
                expDiv.remove();
            });
        }
        addExperienceBtn.addEventListener('click', addExperienceField);
    }

    // Add Projects dynamic fields
    const projectList = document.getElementById('project-list');
    const addProjectBtn = document.getElementById('add-project');
    if (projectList && addProjectBtn) {
        function addProjectField() {
            const idx = projectList.children.length;
            const projDiv = document.createElement('div');
            projDiv.className = 'card mb-2 p-3';
            projDiv.innerHTML = `
                <div class="mb-2"><input type="text" class="form-control" placeholder="Project Title" name="proj_title_${idx}" required></div>
                <div class="mb-2"><textarea class="form-control" placeholder="Description" name="proj_desc_${idx}"></textarea></div>
                <button type="button" class="btn btn-sm btn-danger remove-proj">Remove</button>
            `;
            projectList.appendChild(projDiv);
            projDiv.querySelector('.remove-proj').addEventListener('click', function() {
                projDiv.remove();
            });
        }
        addProjectBtn.addEventListener('click', addProjectField);
    }

    // Add Skills dynamic fields
    const skillsList = document.getElementById('skills-list');
    const addSkillBtn = document.getElementById('add-skill');
    if (skillsList && addSkillBtn) {
        function addSkillField() {
            const idx = skillsList.children.length;
            const skillDiv = document.createElement('div');
            skillDiv.className = 'card mb-2 p-3';
            skillDiv.innerHTML = `
                <div class="mb-2"><input type="text" class="form-control" placeholder="Skill" name="skill_${idx}" required></div>
                <button type="button" class="btn btn-sm btn-danger remove-skill">Remove</button>
            `;
            skillsList.appendChild(skillDiv);
            skillDiv.querySelector('.remove-skill').addEventListener('click', function() {
                skillDiv.remove();
    }
    addSkillBtn.addEventListener('click', addSkillField);
}

// Resume Builder form submission: collect all data and store in hidden input
const resumeForm = document.getElementById('resumeForm');
if (resumeForm) {
    resumeForm.addEventListener('submit', function(event) {
        // Prevent default form submission
        event.preventDefault();
        
        // Basic form validation
        const fullName = document.getElementById('fullName')?.value.trim();
        const email = document.getElementById('email')?.value.trim();
        
        if (!fullName) {
            alert('Please enter your full name');
            document.getElementById('fullName').focus();
            return false;
        }
        
        if (!email) {
            alert('Please enter your email address');
            document.getElementById('email').focus();
            return false;
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            alert('Please enter a valid email address');
            document.getElementById('email').focus();
            return false;
        }

        // Show loading state
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';

        // Gather personal info
        const personal = {
            fullName: fullName,
            email: email,
            phone: document.getElementById('phone')?.value.trim() || '',
            summary: document.getElementById('summary')?.value.trim() || ''
        };

        // Gather education
        const education = [];
        document.querySelectorAll('#education-list > .card').forEach(card => {
            const institution = card.querySelector('input[name^="edu_institution_"]')?.value.trim() || '';
            const degree = card.querySelector('input[name^="edu_degree_"]')?.value.trim() || '';
            const year = card.querySelector('input[name^="edu_year_"]')?.value.trim() || '';
            
            if (institution || degree) {
                education.push({
                    institution: institution,
                    degree: degree,
                    year: year
                });
            }
        });

        // Gather experience
        const experience = [];
        document.querySelectorAll('#experience-list > .card').forEach(card => {
            const company = card.querySelector('input[name^="exp_company_"]')?.value.trim() || '';
            const role = card.querySelector('input[name^="exp_role_"]')?.value.trim() || '';
            
            if (company || role) {
                experience.push({
                    company: company,
                    role: role,
                    duration: card.querySelector('input[name^="exp_duration_"]')?.value.trim() || '',
                    description: card.querySelector('textarea[name^="exp_desc_"]')?.value.trim() || ''
                });
            }
        });

        // Gather projects
        const projects = [];
        document.querySelectorAll('#project-list > .card').forEach(card => {
            const title = card.querySelector('input[name^="proj_title_"]')?.value.trim() || '';
            const description = card.querySelector('textarea[name^="proj_desc_"]')?.value.trim() || '';
            
            if (title) {
                projects.push({
                    title: title,
                    description: description
                });
            }
        });

        // Gather skills
        const skills = [];
        document.querySelectorAll('#skills-list > .card').forEach(card => {
            const skill = card.querySelector('input[name^="skill_"]')?.value.trim() || '';
            if (skill) {
                skills.push(skill);
            var alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            var container = document.querySelector('.container');
            if (container) {
                container.insertBefore(alertDiv, container.firstChild);
                
                // Auto-remove after 5 seconds
                setTimeout(() => {
                    alertDiv.remove();
                }, 5000);
            }
        },

        // Format date
        formatDate: function(date) {
            return new Date(date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        },

        // Debounce function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    };
}); 