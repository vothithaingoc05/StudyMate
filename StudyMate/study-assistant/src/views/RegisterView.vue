<template>
    <div class="register-page">
        <div class="register-card">
            <div class="brand-area">
                <div class="brand-icon">
                    <i class="bi bi-mortarboard-fill"></i>
                </div>

                <div>
                    <h4>StudyMate</h4>
                    <p>AI Study Assistant</p>
                </div>
            </div>

            <div class="form-header">
                <h2>Tạo tài khoản</h2>
                <p>Bắt đầu xây dựng kế hoạch học tập cá nhân của bạn.</p>
            </div>

            <form @submit.prevent="register">
                <div class="form-group">
                    <label>Họ và tên <span>*</span></label>

                    <div class="input-box" :class="{ invalid: errors.fullName }">
                        <i class="bi bi-person"></i>
                        <input v-model.trim="form.fullName" type="text" placeholder="Nhập họ và tên" />
                    </div>

                    <small v-if="errors.fullName" class="error-text">
                        {{ errors.fullName }}
                    </small>
                </div>

                <div class="form-group">
                    <label>Email <span>*</span></label>

                    <div class="input-box" :class="{ invalid: errors.email }">
                        <i class="bi bi-envelope"></i>
                        <input v-model.trim="form.email" type="email" placeholder="Nhập email của bạn" />
                    </div>

                    <small v-if="errors.email" class="error-text">
                        {{ errors.email }}
                    </small>
                </div>

                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="form-group">
                            <label>Mật khẩu <span>*</span></label>

                            <div class="input-box" :class="{ invalid: errors.password }">
                                <i class="bi bi-lock"></i>
                                <input v-model="form.password" :type="showPassword ? 'text' : 'password'"
                                    placeholder="Mật khẩu" />
                            </div>

                            <small v-if="errors.password" class="error-text">
                                {{ errors.password }}
                            </small>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div class="form-group">
                            <label>Xác nhận mật khẩu <span>*</span></label>

                            <div class="input-box" :class="{ invalid: errors.confirmPassword }">
                                <i class="bi bi-shield-lock"></i>
                                <input v-model="form.confirmPassword" :type="showPassword ? 'text' : 'password'"
                                    placeholder="Nhập lại mật khẩu" />
                            </div>

                            <small v-if="errors.confirmPassword" class="error-text">
                                {{ errors.confirmPassword }}
                            </small>
                        </div>
                    </div>
                </div>

                <label class="show-password-row">
                    <input v-model="showPassword" type="checkbox" />
                    <span>Hiển thị mật khẩu</span>
                </label>

                <label class="agree-row">
                    <input v-model="form.agree" type="checkbox" />
                    <span>
                        Tôi đồng ý với điều khoản sử dụng và chính sách bảo mật của StudyMate.
                    </span>
                </label>

                <small v-if="errors.agree" class="error-text agree-error">
                    {{ errors.agree }}
                </small>

                <div v-if="registerError" class="register-error">
                    <i class="bi bi-exclamation-circle-fill"></i>
                    {{ registerError }}
                </div>

                <button class="submit-btn" type="submit" :disabled="isLoading">
                    <template v-if="!isLoading">
                        <i class="bi bi-person-plus-fill"></i>
                        Tạo tài khoản
                    </template>

                    <template v-else>
                        Đang tạo tài khoản...
                    </template>
                </button>
            </form>

            <p class="login-note">
                Đã có tài khoản?
                <RouterLink to="/dang-nhap">Đăng nhập</RouterLink>
            </p>
        </div>

        <div class="decoration">
            <div class="decoration-card">
                <i class="bi bi-stars"></i>
                <h3>StudyMate</h3>
                <p>
                    Quản lý việc học, hỏi đáp AI và nhận nhắc nhở deadline trong một
                    nền tảng duy nhất.
                </p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const form = reactive({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agree: false,
})

const errors = reactive({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agree: '',
})

const showPassword = ref(false)
const registerError = ref('')
const isLoading = ref(false)

const resetErrors = () => {
    errors.fullName = ''
    errors.email = ''
    errors.password = ''
    errors.confirmPassword = ''
    errors.agree = ''
    registerError.value = ''
}

const validateForm = () => {
    resetErrors()
    let valid = true

    if (!form.fullName.trim()) {
        errors.fullName = 'Vui lòng nhập họ và tên.'
        valid = false
    }

    if (!form.email.trim()) {
        errors.email = 'Vui lòng nhập email.'
        valid = false
    }

    if (!form.password) {
        errors.password = 'Vui lòng nhập mật khẩu.'
        valid = false
    } else if (form.password.length < 6) {
        errors.password = 'Mật khẩu phải có ít nhất 6 ký tự.'
        valid = false
    }

    if (!form.confirmPassword) {
        errors.confirmPassword = 'Vui lòng xác nhận mật khẩu.'
        valid = false
    } else if (form.password !== form.confirmPassword) {
        errors.confirmPassword = 'Mật khẩu xác nhận không khớp.'
        valid = false
    }

    if (!form.agree) {
        errors.agree = 'Bạn cần đồng ý với điều khoản để đăng ký.'
        valid = false
    }

    return valid
}

const register = async () => {
    if (!validateForm()) {
        return
    }

    isLoading.value = true
    registerError.value = ''

    try {
        const response = await api.post('/auth/register', {
            full_name: form.fullName.trim(),
            email: form.email.trim(),
            password: form.password,
        })

        router.push({
            path: '/kiem-tra-email',
            query: {
                email: response.data.email,
            },
        })
    } catch (error) {
        if (error.response?.status === 409) {
            registerError.value = error.response.data.detail
        } else if (error.response?.status === 500) {
            registerError.value =
                'Không thể gửi email xác thực. Vui lòng thử lại sau.'
        } else if (!error.response) {
            registerError.value =
                'Không thể kết nối backend. Hãy kiểm tra FastAPI đang chạy.'
        } else {
            registerError.value = 'Đăng ký thất bại. Vui lòng thử lại.'
        }
    } finally {
        isLoading.value = false
    }
}
</script>

<style scoped>
.register-page {
    min-height: 100vh;
    padding: 34px;
    background:
        radial-gradient(circle at 90% 10%, rgba(217, 174, 118, 0.2), transparent 28%),
        radial-gradient(circle at 10% 90%, rgba(185, 130, 76, 0.13), transparent 26%),
        var(--sm-bg);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 55px;
}

.register-card {
    width: 100%;
    max-width: 560px;
    padding: 37px;
    border: 1px solid var(--sm-border);
    border-radius: 25px;
    background: white;
    box-shadow: 0 24px 58px rgba(67, 45, 30, 0.08);
}

.brand-area {
    margin-bottom: 29px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-icon {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    color: white;
    background: var(--sm-primary);
    font-size: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.brand-area h4 {
    margin: 0;
    color: var(--sm-text);
    font-weight: 700;
}

.brand-area p {
    margin: 3px 0 0;
    color: var(--sm-text-soft);
    font-size: 12px;
}

.form-header {
    margin-bottom: 27px;
}

.form-header h2 {
    margin: 0 0 9px;
    color: var(--sm-text);
    font-size: 30px;
    font-weight: 750;
}

.form-header p {
    margin: 0;
    color: var(--sm-text-soft);
}

.form-group {
    margin-bottom: 18px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    color: #5d5148;
    font-size: 14px;
    font-weight: 600;
}

.form-group label span {
    color: var(--sm-danger);
}

.input-box {
    height: 51px;
    padding: 0 13px;
    border: 1px solid var(--sm-border);
    border-radius: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.input-box:focus-within {
    border-color: var(--sm-primary);
    box-shadow: 0 0 0 3px var(--sm-primary-soft);
}

.input-box.invalid {
    border-color: var(--sm-danger);
}

.input-box i {
    color: var(--sm-text-muted);
    font-size: 17px;
}

.input-box input {
    width: 100%;
    border: none;
    outline: none;
}

.error-text {
    display: block;
    margin-top: 6px;
    color: var(--sm-danger);
    font-size: 12px;
}

.show-password-row,
.agree-row {
    color: var(--sm-text-soft);
    font-size: 13px;
    display: flex;
    align-items: flex-start;
    gap: 8px;
}

.show-password-row {
    margin: 1px 0 18px;
}

.agree-row {
    margin-bottom: 4px;
}

.show-password-row input,
.agree-row input {
    margin-top: 2px;
    accent-color: var(--sm-primary);
}

.agree-error {
    margin-bottom: 17px;
}

.register-error {
    margin: 16px 0;
    padding: 12px;
    border-radius: 10px;
    color: var(--sm-danger);
    background: var(--sm-danger-bg);
    font-size: 13px;
}

.submit-btn {
  width: 100%;
  height: 52px;
  margin-top: 19px;
  border: none;
  border-radius: 13px;
  color: white;
  background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
  font-weight: 700;
  box-shadow: 0 11px 22px rgba(185, 130, 76, 0.2);
}

.submit-btn:hover {
  background: linear-gradient(135deg, var(--sm-primary-dark), var(--sm-primary));
}

.submit-btn:disabled {
  cursor: not-allowed;
  background: #d4b38e;
  box-shadow: none;
}

.submit-btn i {
    margin-right: 7px;
}


.login-note {
    margin: 24px 0 0;
    color: var(--sm-text-soft);
    font-size: 14px;
    text-align: center;
}

.login-note a {
    margin-left: 4px;
    color: var(--sm-primary);
    text-decoration: none;
    font-weight: 700;
}

.decoration {
    width: 370px;
}

.decoration-card {
    padding: 40px 35px;
    border-radius: 28px;
    color: #fffaf4;
    background:
        radial-gradient(circle at 86% 12%, rgba(241, 221, 196, 0.26), transparent 28%),
        linear-gradient(145deg, #3b2f2a, #765139, #b9824c);
    box-shadow: 0 26px 55px rgba(90, 58, 33, 0.2);
}

.decoration-card i {
    font-size: 39px;
}

.decoration-card h3 {
    margin: 19px 0 11px;
    font-size: 31px;
    font-weight: 750;
}

.decoration-card p {
    margin: 0;
    color: #f1ddc4;
    line-height: 1.7;
}

@media (max-width: 1000px) {
    .decoration {
        display: none;
    }

    .register-page {
        padding: 20px;
    }
}

@media (max-width: 576px) {
    .register-card {
        padding: 26px 20px;
    }
}
</style>