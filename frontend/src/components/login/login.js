import { ApiService, AuthService } from '../../index.js';

// Login component functionality
export default class Login {
  constructor() {
    this.container = document.getElementById('container');
    this.registerBtn = document.getElementById('register');
    this.loginBtn = document.getElementById('login');
    this.registerForm = document.getElementById('registerForm');
    this.loginForm = document.getElementById('loginForm');
    
    this.init();
  }
  
  init() {
    // Check if already logged in
    if (AuthService.isAuthenticated()) {
      const user = AuthService.getUser();
      this.redirectBasedOnRole(user.role);
      return;
    }
    
    // Toggle animations
    this.registerBtn.addEventListener('click', () => {
      this.container.classList.add("active");
    });
    
    this.loginBtn.addEventListener('click', () => {
      this.container.classList.remove("active");
    });
    
    // Handle Register
    this.registerForm.addEventListener("submit", this.handleRegister.bind(this));
    
    // Handle Login
    this.loginForm.addEventListener("submit", this.handleLogin.bind(this));
    
    // Add form validation
    this.addFormValidation();
  }
  
  // Form validation
  addFormValidation() {
    // Validate name (letters, spaces, min 2 chars)
    const nameInput = this.registerForm.querySelector('input[placeholder="Full Name"]');
    nameInput.addEventListener('input', () => {
      const name = nameInput.value.trim();
      const isValid = /^[A-Za-z\s]{2,}$/.test(name);
      this.setValidationState(nameInput, isValid, 'Name must contain at least 2 letters');
    });
    
    // Validate email (institutional email format)
    const emailInputs = [
      this.registerForm.querySelector('input[placeholder="Institutional Email"]'),
      document.getElementById('loginEmail')
    ];
    
    emailInputs.forEach(input => {
      input.addEventListener('input', () => {
        const email = input.value.trim();
        const isValid = /^[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}$/.test(email);
        this.setValidationState(input, isValid, 'Please enter a valid email address');
      });
    });
    
    // Validate password (min 6 chars, at least 1 number, 1 uppercase)
    const passwordInputs = [
      this.registerForm.querySelector('input[placeholder="Password"]'),
      document.getElementById('loginPassword')
    ];
    
    passwordInputs.forEach(input => {
      input.addEventListener('input', () => {
        const password = input.value.trim();
        const isValid = /^(?=.*[A-Z])(?=.*\d).{6,}$/.test(password);
        this.setValidationState(
          input, 
          isValid, 
          'Password must be at least 6 characters with 1 number and 1 uppercase letter'
        );
      });
    });
  }
  
  setValidationState(input, isValid, errorMessage) {
    // Remove any existing error message
    const existingError = input.parentNode.querySelector('.error-message');
    if (existingError) {
      existingError.remove();
    }
    
    if (!isValid) {
      input.style.borderColor = '#e53935';
      const errorElement = document.createElement('div');
      errorElement.className = 'error-message';
      errorElement.textContent = errorMessage;
      input.parentNode.insertBefore(errorElement, input.nextSibling);
    } else {
      input.style.borderColor = '';
    }
    
    return isValid;
  }
  
  async handleRegister(e) {
    e.preventDefault();
    
    // Show loading indicator
    this.showLoading(this.registerForm);
    
    const name = this.registerForm.querySelector('input[placeholder="Full Name"]').value.trim();
    const email = this.registerForm.querySelector('input[placeholder="Institutional Email"]').value.trim();
    const password = this.registerForm.querySelector('input[placeholder="Password"]').value.trim();
    const role = document.getElementById("registerRole").value;
    
    // Validate all fields
    const isNameValid = this.setValidationState(
      this.registerForm.querySelector('input[placeholder="Full Name"]'),
      /^[A-Za-z\s]{2,}$/.test(name),
      'Name must contain at least 2 letters'
    );
    
    const isEmailValid = this.setValidationState(
      this.registerForm.querySelector('input[placeholder="Institutional Email"]'),
      /^[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}$/.test(email),
      'Please enter a valid email address'
    );
    
    const isPasswordValid = this.setValidationState(
      this.registerForm.querySelector('input[placeholder="Password"]'),
      /^(?=.*[A-Z])(?=.*\d).{6,}$/.test(password),
      'Password must be at least 6 characters with 1 number and 1 uppercase letter'
    );
    
    const isRoleValid = role !== "" && (role === "teacher" || role === "student");
    
    if (!isNameValid || !isEmailValid || !isPasswordValid || !isRoleValid) {
      this.hideLoading(this.registerForm);
      return;
    }
    
    try {
      // Call API to register user
      const response = await ApiService.auth.register(name, email, password, role);
      
      // Store token and user info
      AuthService.setToken(response.token);
      AuthService.setUser(response.user);
      
      // Show success message
      this.showMessage(this.registerForm, 'Registration successful! Redirecting...', 'success');
      
      // Redirect after short delay
      setTimeout(() => {
        this.redirectBasedOnRole(role);
      }, 1500);
      
    } catch (error) {
      this.showMessage(this.registerForm, error.message || 'Registration failed. Please try again.', 'error');
      this.hideLoading(this.registerForm);
    }
  }
  
  async handleLogin(e) {
    e.preventDefault();
    
    // Show loading indicator
    this.showLoading(this.loginForm);
    
    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();
    const role = document.getElementById("loginRole").value;
    
    // Validate fields
    const isEmailValid = this.setValidationState(
      document.getElementById("loginEmail"),
      /^[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}$/.test(email),
      'Please enter a valid email address'
    );
    
    const isPasswordValid = password.length > 0;
    const isRoleValid = role !== "" && (role === "teacher" || role === "student");
    
    if (!isEmailValid || !isPasswordValid || !isRoleValid) {
      this.hideLoading(this.loginForm);
      return;
    }
    
    try {
      // Call API to login
      const response = await ApiService.auth.login(email, password, role);
      
      // Store token and user info
      AuthService.setToken(response.token);
      AuthService.setUser(response.user);
      
      // Show success message
      this.showMessage(this.loginForm, 'Login successful! Redirecting...', 'success');
      
      // Redirect after short delay
      setTimeout(() => {
        this.redirectBasedOnRole(role);
      }, 1500);
      
    } catch (error) {
      this.showMessage(this.loginForm, error.message || 'Invalid credentials. Please try again.', 'error');
      this.hideLoading(this.loginForm);
    }
  }
  
  redirectBasedOnRole(role) {
    if (role === "teacher") {
      window.location.href = "/teacher.html";
    } else if (role === "student") {
      window.location.href = "/student.html";
    }
  }
  
  showLoading(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span>';
  }
  
  hideLoading(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = false;
    submitBtn.innerHTML = form === this.registerForm ? 'Register' : 'Login';
  }
  
  showMessage(form, message, type) {
    // Remove any existing messages
    const existingMessage = form.querySelector('.message');
    if (existingMessage) {
      existingMessage.remove();
    }
    
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}-message`;
    messageElement.textContent = message;
    
    const submitBtn = form.querySelector('button[type="submit"]');
    form.insertBefore(messageElement, submitBtn);
  }
}

// Initialize the login component
new Login();