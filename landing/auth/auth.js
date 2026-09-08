/**
 * JuniorSwipe - Authentication Logic
 */

// ============================================
// TOGGLE PASSWORD VISIBILITY
// ============================================
function setupPasswordToggles() {
    const toggleButtons = document.querySelectorAll('.toggle-password');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const input = button.parentElement.querySelector('input');
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            
            // Cambiar icono (opcional - puedes agregar iconos de ojo abierto/cerrado)
            button.classList.toggle('active');
        });
    });
}

// ============================================
// PASSWORD STRENGTH CHECKER
// ============================================
function checkPasswordStrength(password) {
    let strength = 0;
    const strengthBar = document.querySelector('.strength-bar');
    const strengthText = document.querySelector('.strength-text');
    
    if (!strengthBar) return;
    
    // Criterios de fortaleza
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z\d]/.test(password)) strength++;
    
    // Actualizar barra y texto
    strengthBar.className = 'strength-bar';
    
    if (strength <= 2) {
        strengthBar.classList.add('weak');
        strengthText.textContent = 'Contraseña débil';
        strengthText.style.color = 'var(--error)';
    } else if (strength <= 4) {
        strengthBar.classList.add('medium');
        strengthText.textContent = 'Contraseña media';
        strengthText.style.color = 'var(--warning)';
    } else {
        strengthBar.classList.add('strong');
        strengthText.textContent = 'Contraseña fuerte';
        strengthText.style.color = 'var(--success)';
    }
}

// ============================================
// USER TYPE SELECTOR
// ============================================
function setupUserTypeSelector() {
    const typeButtons = document.querySelectorAll('.type-btn');
    const userTypeInput = document.getElementById('userType');
    
    typeButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            typeButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Update hidden input value
            if (userTypeInput) {
                userTypeInput.value = button.dataset.type;
            }
        });
    });
}

// ============================================
// TOAST NOTIFICATIONS
// ============================================
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// ============================================
// FORM VALIDATION
// ============================================
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password.length >= 8;
}

// ============================================
// LOGIN FORM HANDLER
// ============================================
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(loginForm);
        const email = formData.get('email');
        const password = formData.get('password');
        const remember = formData.get('remember');
        
        // Validaciones
        if (!validateEmail(email)) {
            showToast('Por favor ingresa un email válido', 'error');
            return;
        }
        
        if (!validatePassword(password)) {
            showToast('La contraseña debe tener al menos 8 caracteres', 'error');
            return;
        }
        
        try {
            // Aquí irá tu llamada al backend
            // const response = await fetch('/api/auth/login', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({ email, password, remember })
            // });
            
            // SIMULACIÓN (eliminar en producción)
            console.log('Login attempt:', { email, password, remember });
            
            showToast('Iniciando sesión...', 'success');
            
            // Simular redirección después de login exitoso
            setTimeout(() => {
                window.location.href = '../dashboard.html'; // Cambiar a tu ruta real
            }, 1500);
            
        } catch (error) {
            console.error('Error:', error);
            showToast('Error al iniciar sesión. Intenta de nuevo.', 'error');
        }
    });
}

// ============================================
// REGISTER FORM HANDLER
// ============================================
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    // Password strength checker en tiempo real
    const registerPassword = document.getElementById('registerPassword');
    if (registerPassword) {
        registerPassword.addEventListener('input', (e) => {
            checkPasswordStrength(e.target.value);
        });
    }
    
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(registerForm);
        const fullName = formData.get('fullName');
        const email = formData.get('email');
        const password = formData.get('password');
        const confirmPassword = formData.get('confirmPassword');
        const userType = formData.get('userType');
        const terms = formData.get('terms');
        
        // Validaciones
        if (!fullName || fullName.trim().length < 3) {
            showToast('Por favor ingresa tu nombre completo', 'error');
            return;
        }
        
        if (!validateEmail(email)) {
            showToast('Por favor ingresa un email válido', 'error');
            return;
        }
        
        if (!validatePassword(password)) {
            showToast('La contraseña debe tener al menos 8 caracteres', 'error');
            return;
        }
        
        if (password !== confirmPassword) {
            showToast('Las contraseñas no coinciden', 'error');
            return;
        }
        
        if (!terms) {
            showToast('Debes aceptar los términos y condiciones', 'error');
            return;
        }
        
        try {
            // Aquí irá tu llamada al backend
            // const response = await fetch('/api/auth/register', {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({ fullName, email, password, userType })
            // });
            
            // SIMULACIÓN (eliminar en producción)
            console.log('Register attempt:', { fullName, email, userType });
            
            showToast('Cuenta creada exitosamente! Redirigiendo...', 'success');
            
            // Simular redirección
            setTimeout(() => {
                window.location.href = userType === 'developer' 
                    ? '../dashboard-developer.html' 
                    : '../dashboard-company.html';
            }, 1500);
            
        } catch (error) {
            console.error('Error:', error);
            showToast('Error al crear cuenta. Intenta de nuevo.', 'error');
        }
    });
}

// ============================================
// OAUTH HANDLERS
// ============================================
function handleOAuthLogin(provider) {
    showToast(`Redirigiendo a ${provider}...`, 'info');
    
    // Aquí irá la lógica real de OAuth
    // window.location.href = `/api/auth/${provider}`;
    
    console.log(`OAuth login with ${provider}`);
}

// Google Login/Register
document.getElementById('googleLogin')?.addEventListener('click', () => {
    handleOAuthLogin('google');
});

document.getElementById('googleRegister')?.addEventListener('click', () => {
    handleOAuthLogin('google');
});

// GitHub Login/Register
document.getElementById('githubLogin')?.addEventListener('click', () => {
    handleOAuthLogin('github');
});

document.getElementById('githubRegister')?.addEventListener('click', () => {
    handleOAuthLogin('github');
});

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    setupPasswordToggles();
    setupUserTypeSelector();
});