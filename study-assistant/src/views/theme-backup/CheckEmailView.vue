<template>
    <div class="check-page">
        <div class="check-card">
            <div class="mail-icon">
                <i class="bi bi-envelope-check-fill"></i>
            </div>

            <h1>Kiểm tra email của bạn</h1>

            <p class="description">
                Chúng tôi đã gửi liên kết xác thực đến:
            </p>

            <div class="email-box">
                {{ email }}
            </div>

            <p class="note">
                Nhấn vào nút <strong>Xác thực email</strong> trong thư để kích hoạt tài
                khoản StudyMate. Liên kết có hiệu lực trong 30 phút.
            </p>

            <button class="resend-btn" :disabled="loading" @click="resendEmail">
                <span v-if="!loading">
                    <i class="bi bi-send"></i>
                    Gửi lại email xác thực
                </span>
                <span v-else>Đang gửi lại...</span>
            </button>

            <div v-if="message" class="success-message">
                <i class="bi bi-check-circle-fill"></i>
                {{ message }}
            </div>

            <div v-if="errorMessage" class="error-message">
                <i class="bi bi-exclamation-circle-fill"></i>
                {{ errorMessage }}
            </div>

            <RouterLink to="/dang-nhap" class="login-link">
                Quay lại trang đăng nhập
            </RouterLink>
        </div>
    </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api from '../services/api'

const route = useRoute()

const loading = ref(false)
const message = ref('')
const errorMessage = ref('')

const email = computed(() => {
    return route.query.email || 'địa chỉ email đã đăng ký'
})

const resendEmail = async () => {
    if (!route.query.email) {
        errorMessage.value = 'Không tìm thấy email để gửi lại xác thực.'
        return
    }

    loading.value = true
    message.value = ''
    errorMessage.value = ''

    try {
        const response = await api.post('/auth/resend-verification', {
            email: route.query.email,
        })

        message.value = response.data.message
    } catch (error) {
        errorMessage.value =
            error.response?.data?.detail ||
            'Không thể gửi lại email xác thực. Vui lòng thử lại.'
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.check-page {
    min-height: 100vh;
    padding: 24px;
    background:
        radial-gradient(circle at top left, #e0e7ff, transparent 32%),
        radial-gradient(circle at bottom right, #ede9fe, transparent 30%),
        #f8fafc;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: Inter, Arial, sans-serif;
}

.check-card {
    width: 100%;
    max-width: 510px;
    padding: 44px 39px;
    border: 1px solid #edf0f5;
    border-radius: 26px;
    background: white;
    box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
    text-align: center;
}

.mail-icon {
    width: 86px;
    height: 86px;
    margin: 0 auto 26px;
    border-radius: 50%;
    color: #6366f1;
    background: #eef2ff;
    font-size: 39px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.check-card h1 {
    margin: 0 0 13px;
    color: #111827;
    font-size: 30px;
    font-weight: 750;
}

.description {
    margin: 0 0 16px;
    color: #6b7280;
}

.email-box {
    margin-bottom: 23px;
    padding: 14px;
    border-radius: 12px;
    color: #4338ca;
    background: #eef2ff;
    font-weight: 700;
    word-break: break-word;
}

.note {
    margin: 0 0 29px;
    color: #6b7280;
    font-size: 14px;
    line-height: 1.7;
}

.resend-btn {
    width: 100%;
    height: 53px;
    border: none;
    border-radius: 13px;
    color: white;
    background: #6366f1;
    font-weight: 700;
}

.resend-btn:hover {
    background: #4f46e5;
}

.resend-btn:disabled {
    background: #a5b4fc;
}

.resend-btn i {
    margin-right: 7px;
}

.success-message,
.error-message {
    margin-top: 18px;
    padding: 12px;
    border-radius: 11px;
    font-size: 13px;
}

.success-message {
    color: #15803d;
    background: #f0fdf4;
}

.error-message {
    color: #b91c1c;
    background: #fef2f2;
}

.login-link {
    display: inline-block;
    margin-top: 27px;
    color: #6366f1;
    font-size: 14px;
    font-weight: 700;
    text-decoration: none;
}
</style>