/**
 * Simple tests for AuthFlow JavaScript module
 * These can be run in the browser console or with a testing framework
 */

// Mock DOM elements for testing
function createMockDOM() {
    document.body.innerHTML = `
        <div class="login-container">
            <button class="btn-github">
                <span>Continue with GitHub</span>
                <div class="loading" style="display: none;"></div>
            </button>
            
            <form action="/api/v1/simple_auth/signin" method="POST">
                <div class="form-group">
                    <input type="email" class="form-control" id="email" name="email" required>
                    <input type="password" class="form-control" id="password" name="password" required>
                    <button type="submit" class="btn-primary">Sign In</button>
                </div>
            </form>
        </div>
    `;
}

// Test suite
const AuthFlowTests = {
    
    /**
     * Test email validation
     */
    testEmailValidation() {
        console.log('🧪 Testing email validation...');
        
        const authFlow = new AuthFlow();
        
        // Valid emails
        const validEmails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'test+tag@gmail.com'
        ];
        
        // Invalid emails
        const invalidEmails = [
            'invalid-email',
            '@domain.com',
            'user@',
            'user@domain',
            ''
        ];
        
        validEmails.forEach(email => {
            if (!authFlow.isValidEmail(email)) {
                console.error(`❌ Valid email failed: ${email}`);
            } else {
                console.log(`✅ Valid email passed: ${email}`);
            }
        });
        
        invalidEmails.forEach(email => {
            if (authFlow.isValidEmail(email)) {
                console.error(`❌ Invalid email passed: ${email}`);
            } else {
                console.log(`✅ Invalid email failed correctly: ${email}`);
            }
        });
    },
    
    /**
     * Test form validation
     */
    testFormValidation() {
        console.log('🧪 Testing form validation...');
        
        createMockDOM();
        const authFlow = new AuthFlow();
        const form = document.querySelector('form');
        
        // Test empty form
        const isValidEmpty = authFlow.validateForm(form);
        if (isValidEmpty) {
            console.error('❌ Empty form should not be valid');
        } else {
            console.log('✅ Empty form correctly invalid');
        }
        
        // Test with valid data
        document.getElementById('email').value = 'test@example.com';
        document.getElementById('password').value = 'password123';
        
        const isValidFilled = authFlow.validateForm(form);
        if (!isValidFilled) {
            console.error('❌ Valid form should be valid');
        } else {
            console.log('✅ Valid form correctly valid');
        }
    },
    
    /**
     * Test device fingerprinting
     */
    testDeviceFingerprint() {
        console.log('🧪 Testing device fingerprinting...');
        
        const authFlow = new AuthFlow();
        const fingerprint = authFlow.getDeviceFingerprint();
        
        const requiredFields = ['screen', 'timezone', 'language', 'platform', 'userAgent', 'canvas'];
        
        requiredFields.forEach(field => {
            if (!fingerprint[field]) {
                console.error(`❌ Missing fingerprint field: ${field}`);
            } else {
                console.log(`✅ Fingerprint field present: ${field}`);
            }
        });
        
        console.log('📋 Device fingerprint:', fingerprint);
    },
    
    /**
     * Test UI interactions
     */
    testUIInteractions() {
        console.log('🧪 Testing UI interactions...');
        
        createMockDOM();
        const authFlow = new AuthFlow();
        
        // Test GitHub button loading
        const githubBtn = document.querySelector('.btn-github');
        const span = githubBtn.querySelector('span');
        const loading = githubBtn.querySelector('.loading');
        
        // Simulate button click
        authFlow.showButtonLoading(githubBtn, span, loading);
        
        if (span.style.display === 'none' && loading.style.display === 'block') {
            console.log('✅ GitHub button loading state works');
        } else {
            console.error('❌ GitHub button loading state failed');
        }
        
        // Reset button
        authFlow.resetButtonLoading(githubBtn, span, loading, 'Continue with GitHub');
        
        if (span.style.display === 'block' && loading.style.display === 'none') {
            console.log('✅ GitHub button reset works');
        } else {
            console.error('❌ GitHub button reset failed');
        }
    },
    
    /**
     * Test error handling
     */
    testErrorHandling() {
        console.log('🧪 Testing error handling...');
        
        createMockDOM();
        const authFlow = new AuthFlow();
        const emailInput = document.getElementById('email');
        
        // Show error
        authFlow.showFieldError(emailInput, 'Test error message');
        
        const errorElement = emailInput.parentNode.querySelector('.field-error');
        if (errorElement && errorElement.textContent.includes('Test error message')) {
            console.log('✅ Field error display works');
        } else {
            console.error('❌ Field error display failed');
        }
        
        // Clear error
        authFlow.clearFieldError(emailInput);
        
        const clearedError = emailInput.parentNode.querySelector('.field-error');
        if (!clearedError) {
            console.log('✅ Field error clearing works');
        } else {
            console.error('❌ Field error clearing failed');
        }
    },
    
    /**
     * Test alert notifications
     */
    testAlertNotifications() {
        console.log('🧪 Testing alert notifications...');
        
        const authFlow = new AuthFlow();
        
        // Test success alert
        authFlow.showSuccess('Test success message');
        
        setTimeout(() => {
            const successAlert = document.querySelector('.alert.alert-success');
            if (successAlert) {
                console.log('✅ Success alert works');
                successAlert.remove(); // Clean up
            } else {
                console.error('❌ Success alert failed');
            }
        }, 100);
        
        // Test error alert
        authFlow.showError('Test error message');
        
        setTimeout(() => {
            const errorAlert = document.querySelector('.alert.alert-error');
            if (errorAlert) {
                console.log('✅ Error alert works');
                errorAlert.remove(); // Clean up
            } else {
                console.error('❌ Error alert failed');
            }
        }, 100);
    },
    
    /**
     * Run all tests
     */
    runAllTests() {
        console.log('🚀 Running AuthFlow tests...\n');
        
        this.testEmailValidation();
        console.log('');
        
        this.testFormValidation();
        console.log('');
        
        this.testDeviceFingerprint();
        console.log('');
        
        this.testUIInteractions();
        console.log('');
        
        this.testErrorHandling();
        console.log('');
        
        this.testAlertNotifications();
        console.log('');
        
        console.log('✨ All tests completed!');
    }
};

// Performance testing
const PerformanceTests = {
    
    /**
     * Test initialization performance
     */
    testInitPerformance() {
        console.log('⚡ Testing initialization performance...');
        
        const startTime = performance.now();
        const authFlow = new AuthFlow();
        const endTime = performance.now();
        
        const initTime = endTime - startTime;
        console.log(`📊 Initialization time: ${initTime.toFixed(2)}ms`);
        
        if (initTime < 10) {
            console.log('✅ Fast initialization');
        } else if (initTime < 50) {
            console.log('⚠️ Moderate initialization time');
        } else {
            console.error('❌ Slow initialization');
        }
    },
    
    /**
     * Test validation performance
     */
    testValidationPerformance() {
        console.log('⚡ Testing validation performance...');
        
        createMockDOM();
        const authFlow = new AuthFlow();
        const form = document.querySelector('form');
        
        // Fill form with data
        document.getElementById('email').value = 'test@example.com';
        document.getElementById('password').value = 'password123';
        
        const iterations = 1000;
        const startTime = performance.now();
        
        for (let i = 0; i < iterations; i++) {
            authFlow.validateForm(form);
        }
        
        const endTime = performance.now();
        const avgTime = (endTime - startTime) / iterations;
        
        console.log(`📊 Average validation time: ${avgTime.toFixed(4)}ms`);
        
        if (avgTime < 1) {
            console.log('✅ Fast validation');
        } else if (avgTime < 5) {
            console.log('⚠️ Moderate validation speed');
        } else {
            console.error('❌ Slow validation');
        }
    }
};

// Export for use in browser console
if (typeof window !== 'undefined') {
    window.AuthFlowTests = AuthFlowTests;
    window.PerformanceTests = PerformanceTests;
}

// Auto-run tests if in test environment
if (typeof process !== 'undefined' && process.env.NODE_ENV === 'test') {
    AuthFlowTests.runAllTests();
    PerformanceTests.testInitPerformance();
    PerformanceTests.testValidationPerformance();
}

console.log(`
🧪 AuthFlow Test Suite Loaded!

Run tests in browser console:
- AuthFlowTests.runAllTests()        // Run all functionality tests
- PerformanceTests.testInitPerformance()    // Test initialization speed
- PerformanceTests.testValidationPerformance()  // Test validation speed

Individual tests:
- AuthFlowTests.testEmailValidation()
- AuthFlowTests.testFormValidation()
- AuthFlowTests.testDeviceFingerprint()
- AuthFlowTests.testUIInteractions()
- AuthFlowTests.testErrorHandling()
- AuthFlowTests.testAlertNotifications()
`);
