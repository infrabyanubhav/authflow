/**
 * AuthFlow - Authentication JavaScript Module
 * Handles login form functionality, OAuth flows, and UI interactions
 */

class AuthFlow {
    constructor() {
        this.init();
    }

    /**
     * Initialize the authentication system
     */
    init() {
        this.handleOAuthCallback();
        this.bindEvents();
        this.setupFormValidation();
        this.initializeUI();
        console.log('AuthFlow initialized successfully');
    }

    /**
     * Handle OAuth callback if present in URL
     */
    handleOAuthCallback() {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        
        if (code && window.location.pathname === '/') {
            console.log('OAuth callback detected at root, redirecting to proper handler...');
            // Redirect to the proper callback URL
            window.location.href = `/api/v1/github_auth/callback?code=${code}`;
        }
    }

    /**
     * Bind all event listeners
     */
    bindEvents() {
        // GitHub OAuth button
        const githubBtn = document.querySelector('.btn-github');

        
        if (githubBtn) {
            githubBtn.addEventListener('click', this.handleGitHubLogin.bind(this));
        }

        // Email/Password form
        const loginForm = document.querySelector('form');
        if (loginForm) {
            loginForm.addEventListener('submit', this.handleFormSubmit.bind(this));
        }

        // Input field enhancements
        const inputs = document.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.addEventListener('focus', this.handleInputFocus.bind(this));
            input.addEventListener('blur', this.handleInputBlur.bind(this));
            input.addEventListener('input', this.handleInputChange.bind(this));
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyboardShortcuts.bind(this));
    }

    /**
     * Handle GitHub OAuth login
     */
    handleGitHubLogin(event) {
        // Don't prevent default - let the link work naturally
        const button = event.currentTarget;
        const span = button.querySelector('span');
        const loading = button.querySelector('.loading');
        
        // Show loading state
        this.showButtonLoading(button, span, loading);
        
        // Add analytics or logging here if needed
        this.logEvent('github_oauth_initiated');
        
        // Let the browser handle the navigation naturally
        console.log('GitHub OAuth initiated, following link...');
    }

    /**
     * Handle form submission
     */
    async handleFormSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitBtn = form.querySelector('.btn-primary');
        const formData = new FormData(form);
        
        // Validate form before submission
        if (!this.validateForm(form)) {
            return;
        }

        // Show loading state
        this.showButtonLoading(submitBtn, null, null, 'Signing In...');
        
        try {
            // Log the attempt
            this.logEvent('email_login_attempted');
            
            // Submit the form
            const response = await this.submitForm(form.action, formData);
            
            if (response.ok) {
                this.logEvent('email_login_success');
                this.showSuccess('Login successful! Redirecting...');
                
                // Handle successful login
                setTimeout(() => {
                    window.location.href = response.redirectURL || '/api/v1/welcome';
                }, 1500);
            } else {
                throw new Error('Login failed');
            }
            
        } catch (error) {
            this.logEvent('email_login_failed', { error: error.message });
            this.showError('Login failed. Please check your credentials and try again.');
            this.resetButtonLoading(submitBtn, null, null, 'Sign In');
        }
    }

    /**
     * Submit form data
     */
    async submitForm(action, formData) {
        return fetch(action, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
    }

    /**
     * Validate form inputs
     */
    validateForm(form) {
        const email = form.querySelector('#email');
        const password = form.querySelector('#password');
        let isValid = true;

        // Clear previous errors
        this.clearErrors();

        // Email validation
        if (!email.value.trim()) {
            this.showFieldError(email, 'Email is required');
            isValid = false;
        } else if (!this.isValidEmail(email.value)) {
            this.showFieldError(email, 'Please enter a valid email address');
            isValid = false;
        }

        // Password validation
        if (!password.value.trim()) {
            this.showFieldError(password, 'Password is required');
            isValid = false;
        } else if (password.value.length < 6) {
            this.showFieldError(password, 'Password must be at least 6 characters');
            isValid = false;
        }

        return isValid;
    }

    /**
     * Setup real-time form validation
     */
    setupFormValidation() {
        const emailInput = document.querySelector('#email');
        const passwordInput = document.querySelector('#password');

        if (emailInput) {
            emailInput.addEventListener('blur', () => {
                if (emailInput.value && !this.isValidEmail(emailInput.value)) {
                    this.showFieldError(emailInput, 'Please enter a valid email address');
                } else {
                    this.clearFieldError(emailInput);
                }
            });
        }

        if (passwordInput) {
            passwordInput.addEventListener('input', () => {
                if (passwordInput.value.length > 0 && passwordInput.value.length < 6) {
                    this.showFieldError(passwordInput, 'Password must be at least 6 characters');
                } else {
                    this.clearFieldError(passwordInput);
                }
            });
        }
    }

    /**
     * Handle input field focus
     */
    handleInputFocus(event) {
        const input = event.target;
        const formGroup = input.closest('.form-group');
        
        if (formGroup) {
            formGroup.classList.add('focused');
        }
        
        // Clear any existing errors when user starts typing
        this.clearFieldError(input);
    }

    /**
     * Handle input field blur
     */
    handleInputBlur(event) {
        const input = event.target;
        const formGroup = input.closest('.form-group');
        
        if (formGroup) {
            formGroup.classList.remove('focused');
        }
    }

    /**
     * Handle input change
     */
    handleInputChange(event) {
        const input = event.target;
        
        // Clear errors as user types
        if (input.value.trim()) {
            this.clearFieldError(input);
        }
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(event) {
        // Enter key on form
        if (event.key === 'Enter' && event.target.tagName === 'INPUT') {
            const form = event.target.closest('form');
            if (form) {
                form.dispatchEvent(new Event('submit'));
            }
        }

        // Escape key to clear errors
        if (event.key === 'Escape') {
            this.clearErrors();
        }
    }

    /**
     * Initialize UI enhancements
     */
    initializeUI() {
        // Add smooth scrolling
        document.documentElement.style.scrollBehavior = 'smooth';
        
        // Add focus trap for accessibility
        this.setupFocusTrap();
        
        // Initialize tooltips if needed
        this.initializeTooltips();
        
        // Set up auto-focus on first input
        const firstInput = document.querySelector('.form-control');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 500);
        }
    }

    /**
     * Setup focus trap for accessibility
     */
    setupFocusTrap() {
        const focusableElements = document.querySelectorAll(
            'input, button, select, textarea, a[href], [tabindex]:not([tabindex="-1"])'
        );
        
        if (focusableElements.length > 0) {
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            document.addEventListener('keydown', (event) => {
                if (event.key === 'Tab') {
                    if (event.shiftKey && document.activeElement === firstElement) {
                        event.preventDefault();
                        lastElement.focus();
                    } else if (!event.shiftKey && document.activeElement === lastElement) {
                        event.preventDefault();
                        firstElement.focus();
                    }
                }
            });
        }
    }

    /**
     * Initialize tooltips
     */
    initializeTooltips() {
        // Add tooltips for form fields if Bootstrap tooltips are available
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        }
    }

    /**
     * Show button loading state
     */
    showButtonLoading(button, textElement, loadingElement, loadingText = 'Loading...') {
        button.disabled = true;
        
        if (textElement && loadingElement) {
            textElement.style.display = 'none';
            loadingElement.style.display = 'block';
        } else {
            button.innerHTML = `<div class="loading" style="display: block; margin: 0 auto;"></div>`;
            if (loadingText) {
                button.innerHTML += `<span style="margin-left: 10px;">${loadingText}</span>`;
            }
        }
    }

    /**
     * Reset button loading state
     */
    resetButtonLoading(button, textElement, loadingElement, originalText) {
        button.disabled = false;
        
        if (textElement && loadingElement) {
            textElement.style.display = 'block';
            loadingElement.style.display = 'none';
        } else {
            button.innerHTML = originalText;
        }
    }

    /**
     * Show field-specific error
     */
    showFieldError(input, message) {
        this.clearFieldError(input);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.style.cssText = `
            color: #ef4444;
            font-size: 0.85rem;
            margin-top: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        `;
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i>${message}`;
        
        input.style.borderColor = '#ef4444';
        input.parentNode.appendChild(errorDiv);
    }

    /**
     * Clear field-specific error
     */
    clearFieldError(input) {
        const existingError = input.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
        input.style.borderColor = '';
    }

    /**
     * Clear all errors
     */
    clearErrors() {
        const errors = document.querySelectorAll('.field-error, .alert-error');
        errors.forEach(error => error.remove());
        
        const inputs = document.querySelectorAll('.form-control');
        inputs.forEach(input => {
            input.style.borderColor = '';
        });
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    /**
     * Show error message
     */
    showError(message) {
        this.showAlert(message, 'error');
    }

    /**
     * Show alert message
     */
    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 0.5rem;
            max-width: 400px;
            animation: slideIn 0.3s ease;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
        `;
        
        const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle';
        alertDiv.innerHTML = `<i class="fas fa-${icon}"></i>${message}`;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => alertDiv.remove(), 300);
            }
        }, 5000);
    }

    /**
     * Validate email format
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Log events for analytics
     */
    logEvent(eventName, data = {}) {
        // You can integrate with analytics services here
        console.log(`AuthFlow Event: ${eventName}`, data);
        
        // Example: Send to analytics service
        // if (window.gtag) {
        //     gtag('event', eventName, data);
        // }
    }

    /**
     * Get device fingerprint (basic implementation)
     */
    getDeviceFingerprint() {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        ctx.textBaseline = 'top';
        ctx.font = '14px Arial';
        ctx.fillText('Device fingerprint', 2, 2);
        
        return {
            screen: `${screen.width}x${screen.height}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            language: navigator.language,
            platform: navigator.platform,
            userAgent: navigator.userAgent,
            canvas: canvas.toDataURL()
        };
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .form-group.focused .form-control {
        border-color: #667eea !important;
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1) !important;
    }
    
    .form-control {
        transition: all 0.3s ease;
    }
`;
document.head.appendChild(style);

// Initialize AuthFlow when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.authFlow = new AuthFlow();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthFlow;
}
