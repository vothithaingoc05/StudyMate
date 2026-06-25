<template>
    <div class="auth-page">
        <div class="auth-left">
            <div class="brand">
                <div class="brand-icon">
                    <i class="bi bi-mortarboard-fill"></i>
                </div>

                <div>
                    <h4>StudyMate</h4>
                    <p>AI Study Assistant</p>
                </div>
            </div>

            <div class="hero-content">
                <span class="hero-badge">
                    <i class="bi bi-stars"></i>
                    Trợ lý học tập cá nhân
                </span>

                <h1>Học tập thông minh hơn với AI</h1>

                <p class="hero-description">
                    Quản lý lịch học, deadline, tài liệu và nhận hỗ trợ hỏi đáp
                    dựa trên nội dung bạn đã lưu.
                </p>

                <div class="feature-list">
                    <div class="feature-item">
                        <div class="feature-icon">
                            <i class="bi bi-calendar-check-fill"></i>
                        </div>
                        <div>
                            <strong>Lập kế hoạch học tập</strong>
                            <p>Theo dõi lịch ôn tập và deadline quan trọng.</p>
                        </div>
                    </div>

                    <div class="feature-item">
                        <div class="feature-icon">
                            <i class="bi bi-robot"></i>
                        </div>
                        <div>
                            <strong>Chatbot hỏi đáp</strong>
                            <p>Giải thích bài học dựa trên tài liệu cá nhân.</p>
                        </div>
                    </div>

                    <div class="feature-item">
                        <div class="feature-icon">
                            <i class="bi bi-bell-fill"></i>
                        </div>
                        <div>
                            <strong>Nhắc nhở qua Email</strong>
                            <p>Không bỏ lỡ bài tập và lịch thi sắp tới.</p>
                        </div>
                    </div>
                </div>
            </div>

            <p class="copyright">© 2026 StudyMate. Personal Study Assistant.</p>
        </div>

        <div class="auth-right">
            <div class="login-card">
                <div class="mobile-brand">
                    <div class="brand-icon">
                        <i class="bi bi-mortarboard-fill"></i>
                    </div>
                    <h4>StudyMate</h4>
                </div>

                <div class="form-header">
                    <h2>Đăng nhập</h2>
                    <p>Chào mừng bạn quay lại hệ thống học tập.</p>
                </div>

                <div class="demo-account">
                    <div class="demo-icon">
                        <i class="bi bi-info-circle-fill"></i>
                    </div>

                    <div>
                        <strong>Tài khoản demo</strong>
                        <p>vothithaingoc072005@gmail.com</p>
                        <p>Mật khẩu: 123456</p>
                    </div>

                    <button type="button" @click="fillDemoAccount">
                        Dùng ngay
                    </button>
                </div>

                <form @submit.prevent="login">
                    <div class="form-group">
                        <label>Email</label>

                        <div class="input-box" :class="{ invalid: errors.email }">
                            <i class="bi bi-envelope"></i>
                            <input v-model.trim="form.email" type="email" placeholder="Nhập email của bạn" />
                        </div>

                        <small v-if="errors.email" class="error-text">
                            {{ errors.email }}
                        </small>
                    </div>

                    <div class="form-group">
                        <div class="label-row">
                            <label>Mật khẩu</label>
                            <button type="button" class="forgot-link">
                                Quên mật khẩu?
                            </button>
                        </div>

                        <div class="input-box" :class="{ invalid: errors.password }">
                            <i class="bi bi-lock"></i>

                            <input v-model="form.password" :type="showPassword ? 'text' : 'password'"
                                placeholder="Nhập mật khẩu" />

                            <button type="button" class="toggle-password" @click="showPassword = !showPassword">
                                <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                            </button>
                        </div>

                        <small v-if="errors.password" class="error-text">
                            {{ errors.password }}
                        </small>
                    </div>

                    <label class="remember-row">
                        <input v-model="form.remember" type="checkbox" />
                        <span>Ghi nhớ đăng nhập</span>
                    </label>

                    <div v-if="loginError" class="login-error">
                        <i class="bi bi-exclamation-circle-fill"></i>
                        {{ loginError }}
                    </div>

                    <button class="submit-btn" type="submit" :disabled="isLoading">
                        <span v-if="!isLoading">Đăng nhập</span>
                        <span v-else class="loading-text">
                            <span class="spinner"></span>
                            Đang đăng nhập...
                        </span>
                    </button>
                </form>

                <div class="register-note">
                    Chưa có tài khoản?
                    <RouterLink to="/dang-ky">Đăng ký ngay</RouterLink>
                </div>
            </div>
        </div>

        <div v-if="toastMessage" class="toast-message">
            <i class="bi bi-check-circle-fill"></i>
            {{ toastMessage }}
        </div>
    </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import api from '../services/api'
import { authStore } from '../stores/auth'

const router = useRouter()

const demoAccount = {
    email: 'vothithaingoc072005@gmail.com',
    password: '123456',
}

const form = reactive({
    email: '',
    password: '',
    remember: false,
})

const errors = reactive({
    email: '',
    password: '',
})

const showPassword = ref(false)
const loginError = ref('')
const isLoading = ref(false)
const toastMessage = ref('')

const fillDemoAccount = () => {
    form.email = demoAccount.email
    form.password = demoAccount.password
    errors.email = ''
    errors.password = ''
    loginError.value = ''
}

const resetErrors = () => {
    errors.email = ''
    errors.password = ''
    loginError.value = ''
}

const validateForm = () => {
    resetErrors()
    let valid = true

    if (!form.email.trim()) {
        errors.email = 'Vui lòng nhập email.'
        valid = false
    }

    if (!form.password) {
        errors.password = 'Vui lòng nhập mật khẩu.'
        valid = false
    }

    return valid
}

const login = async () => {
    if (!validateForm()) {
        return
    }

    isLoading.value = true
    loginError.value = ''

    try {
        const response = await api.post('/auth/login', {
            email: form.email.trim(),
            password: form.password,
        })

        authStore.setUser(response.data.user)

        toastMessage.value = 'Đăng nhập thành công.'

        setTimeout(() => {
            router.push('/dashboard')
        }, 350)
    } catch (error) {
        if (error.response?.status === 401) {
            loginError.value = 'Email hoặc mật khẩu không chính xác.'
        } else if (error.response?.status === 403) {
            loginError.value =
                error.response.data.detail ||
                'Tài khoản chưa được xác thực. Vui lòng kiểm tra email.'
        } else if (!error.response) {
            loginError.value =
                'Không thể kết nối backend. Hãy kiểm tra FastAPI đang chạy.'
        } else {
            loginError.value = 'Đăng nhập thất bại. Vui lòng thử lại.'
        }
    } finally {
        isLoading.value = false
    }
}
</script>

<style scoped>
.auth-page {
    min-height: 100vh;
    display: flex;
    font-family: Inter, Arial, sans-serif;
    background: #f8fafc;
}

.auth-left {
    position: relative;
    width: 52%;
    min-height: 100vh;
    padding: 36px 54px;
    color: white;
    overflow: hidden;
    background:
        radial-gradient(circle at 18% 18%, rgba(129, 140, 248, 0.36), transparent 30%),
        radial-gradient(circle at 85% 78%, rgba(167, 139, 250, 0.30), transparent 29%),
        linear-gradient(140deg, #111827 0%, #312e81 50%, #4f46e5 100%);
    display: flex;
    flex-direction: column;
}

.auth-left::after {
    position: absolute;
    content: '';
    right: -130px;
    bottom: -130px;
    width: 370px;
    height: 370px;
    border: 1px solid rgba(255, 255, 255, 0.13);
    border-radius: 50%;
}

.brand {
    position: relative;
    z-index: 1;
    display: flex;
    align-items: center;
    gap: 13px;
}

.brand-icon {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    color: white;
    background: #6366f1;
    font-size: 24px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.brand h4 {
    margin: 0;
    font-weight: 700;
}

.brand p {
    margin: 3px 0 0;
    color: #cbd5e1;
    font-size: 12px;
}

.hero-content {
    position: relative;
    z-index: 1;
    max-width: 530px;
    margin: auto 0;
}

.hero-badge {
    width: fit-content;
    padding: 8px 13px;
    border-radius: 24px;
    background: rgba(255, 255, 255, 0.12);
    color: #e0e7ff;
    font-size: 13px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 7px;
}

.hero-content h1 {
    margin: 21px 0 16px;
    font-size: 46px;
    line-height: 1.18;
    font-weight: 750;
}

.hero-description {
    margin: 0 0 38px;
    color: #cbd5e1;
    font-size: 16px;
    line-height: 1.7;
}

.feature-list {
    display: flex;
    flex-direction: column;
    gap: 21px;
}

.feature-item {
    display: flex;
    align-items: center;
    gap: 15px;
}

.feature-icon {
    width: 48px;
    height: 48px;
    flex-shrink: 0;
    border-radius: 14px;
    color: white;
    background: rgba(99, 102, 241, 0.6);
    font-size: 22px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.feature-item strong {
    display: block;
    margin-bottom: 4px;
    font-size: 15px;
}

.feature-item p {
    margin: 0;
    color: #cbd5e1;
    font-size: 13px;
}

.copyright {
    position: relative;
    z-index: 1;
    margin: auto 0 0;
    color: #94a3b8;
    font-size: 13px;
}

.auth-right {
    width: 48%;
    min-height: 100vh;
    padding: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.login-card {
    width: 100%;
    max-width: 448px;
}

.mobile-brand {
    display: none;
}

.form-header {
    margin-bottom: 27px;
}

.form-header h2 {
    margin: 0 0 9px;
    color: #111827;
    font-size: 32px;
    font-weight: 750;
}

.form-header p {
    margin: 0;
    color: #6b7280;
}

.demo-account {
    margin-bottom: 25px;
    padding: 13px 14px;
    border: 1px solid #e0e7ff;
    border-radius: 14px;
    background: #eef2ff;
    display: flex;
    align-items: center;
    gap: 11px;
}

.demo-icon {
    color: #6366f1;
    font-size: 22px;
}

.demo-account div:nth-child(2) {
    flex: 1;
}

.demo-account strong {
    display: block;
    color: #312e81;
    font-size: 13px;
}

.demo-account p {
    margin: 2px 0 0;
    color: #4f46e5;
    font-size: 12px;
}

.demo-account button {
    border: none;
    color: #4338ca;
    background: transparent;
    font-size: 12px;
    font-weight: 700;
}

.form-group {
    margin-bottom: 19px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    color: #374151;
    font-size: 14px;
    font-weight: 600;
}

.label-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.forgot-link {
    margin-bottom: 8px;
    border: none;
    color: #6366f1;
    background: transparent;
    font-size: 13px;
    font-weight: 600;
}

.input-box {
    height: 52px;
    padding: 0 14px;
    border: 1px solid #e5e7eb;
    border-radius: 13px;
    background: white;
    display: flex;
    align-items: center;
    gap: 11px;
}

.input-box:focus-within {
    border-color: #6366f1;
    box-shadow: 0 0 0 3px #eef2ff;
}

.input-box.invalid {
    border-color: #dc2626;
}

.input-box>i {
    color: #9ca3af;
    font-size: 18px;
}

.input-box input {
    flex: 1;
    border: none;
    outline: none;
    color: #111827;
}

.toggle-password {
    border: none;
    color: #6b7280;
    background: transparent;
}

.error-text {
    display: block;
    margin-top: 6px;
    color: #dc2626;
    font-size: 12px;
}

.remember-row {
    margin: 5px 0 22px;
    color: #4b5563;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.remember-row input {
    width: 16px;
    height: 16px;
    accent-color: #6366f1;
}

.login-error {
    margin-bottom: 17px;
    padding: 12px 14px;
    border-radius: 11px;
    color: #b91c1c;
    background: #fef2f2;
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.submit-btn {
    width: 100%;
    height: 52px;
    border: none;
    border-radius: 13px;
    color: white;
    background: #6366f1;
    font-weight: 700;
}

.submit-btn:hover {
    background: #4f46e5;
}

.submit-btn:disabled {
    background: #a5b4fc;
}

.loading-text {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 9px;
}

.spinner {
    width: 17px;
    height: 17px;
    border: 2px solid rgba(255, 255, 255, 0.42);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
}

.register-note {
    margin-top: 25px;
    color: #6b7280;
    text-align: center;
    font-size: 14px;
}

.register-note a {
    margin-left: 4px;
    color: #6366f1;
    font-weight: 700;
    text-decoration: none;
}

.toast-message {
    position: fixed;
    top: 27px;
    right: 27px;
    z-index: 500;
    padding: 14px 18px;
    border-radius: 11px;
    color: white;
    background: #16a34a;
    display: flex;
    align-items: center;
    gap: 9px;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

@media (max-width: 1000px) {
    .auth-left {
        display: none;
    }

    .auth-right {
        width: 100%;
        padding: 25px;
    }

    .mobile-brand {
        margin-bottom: 36px;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .mobile-brand h4 {
        margin: 0;
        color: #111827;
        font-weight: 700;
    }
}
</style>