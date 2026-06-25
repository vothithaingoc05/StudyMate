<template>
  <div class="verify-page">
    <div class="verify-card">
      <div class="brand">
        <div class="brand-icon">
          <i class="bi bi-mortarboard-fill"></i>
        </div>

        <div>
          <h4>StudyMate</h4>
          <p>AI Study Assistant</p>
        </div>
      </div>

      <!-- Đang kiểm tra -->
      <div v-if="status === 'loading'" class="state-content">
        <div class="loading-circle">
          <span class="spinner"></span>
        </div>

        <h2>Đang xác thực email...</h2>
        <p>
          Vui lòng chờ trong giây lát, hệ thống đang kiểm tra liên kết xác thực
          của bạn.
        </p>
      </div>

      <!-- Thành công -->
      <div v-else-if="status === 'success'" class="state-content">
        <div class="success-circle">
          <i class="bi bi-check-lg"></i>
        </div>

        <h2>Xác thực email thành công!</h2>
        <p>
          Tài khoản của bạn đã được kích hoạt. Bây giờ bạn có thể đăng nhập và
          bắt đầu sử dụng StudyMate.
        </p>

        <RouterLink to="/dang-nhap" class="primary-btn">
          <i class="bi bi-box-arrow-in-right"></i>
          Đăng nhập ngay
        </RouterLink>
      </div>

      <!-- Link đã dùng trước đó -->
      <div v-else-if="status === 'verified'" class="state-content">
        <div class="info-circle">
          <i class="bi bi-info-lg"></i>
        </div>

        <h2>Email đã được xác thực</h2>
        <p>
          Liên kết này đã được sử dụng trước đó. Tài khoản của bạn hiện đã có
          thể đăng nhập.
        </p>

        <RouterLink to="/dang-nhap" class="primary-btn">
          Đăng nhập ngay
        </RouterLink>
      </div>

      <!-- Lỗi hoặc hết hạn -->
      <div v-else class="state-content">
        <div class="error-circle">
          <i class="bi bi-x-lg"></i>
        </div>

        <h2>Không thể xác thực email</h2>
        <p>{{ errorMessage }}</p>

        <RouterLink to="/dang-nhap" class="secondary-btn">
          Quay về đăng nhập
        </RouterLink>
      </div>
    </div>

    <div class="side-panel">
      <div class="side-content">
        <i class="bi bi-envelope-check-fill"></i>
        <h1>Xác thực tài khoản</h1>
        <p>
          Bảo vệ tài khoản và đảm bảo bạn nhận được các thông báo học tập,
          deadline và lịch thi quan trọng.
        </p>

        <div class="feature">
          <i class="bi bi-shield-check"></i>
          <span>Email được xác thực an toàn</span>
        </div>

        <div class="feature">
          <i class="bi bi-bell"></i>
          <span>Nhận nhắc nhở học tập đúng địa chỉ</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import api from '../services/api'

const route = useRoute()

const status = ref('loading')
const errorMessage = ref('Liên kết xác thực không hợp lệ hoặc đã hết hạn.')

const verifyEmail = async () => {
  const token = route.query.token

  if (!token) {
    status.value = 'error'
    errorMessage.value = 'Liên kết xác thực không có mã token.'
    return
  }

  try {
    const response = await api.get('/auth/verify-email', {
      params: { token },
    })

    if (response.data.message.includes('trước đó')) {
      status.value = 'verified'
    } else {
      status.value = 'success'
    }
  } catch (error) {
    status.value = 'error'

    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else if (!error.response) {
      errorMessage.value =
        'Không thể kết nối backend. Vui lòng kiểm tra FastAPI đang chạy.'
    }
  }
}

onMounted(() => {
  verifyEmail()
})
</script>

<style scoped>
.verify-page {
  min-height: 100vh;
  padding: 34px;
  background:
    radial-gradient(circle at 14% 12%, #e0e7ff, transparent 28%),
    radial-gradient(circle at 88% 86%, #ede9fe, transparent 30%),
    #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 34px;
  font-family: Inter, Arial, sans-serif;
}

.verify-card {
  width: 100%;
  max-width: 530px;
  min-height: 570px;
  padding: 38px;
  border: 1px solid #edf0f5;
  border-radius: 26px;
  background: white;
  box-shadow: 0 25px 65px rgba(15, 23, 42, 0.08);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 62px;
}

.brand-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  color: white;
  background: #6366f1;
  font-size: 23px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand h4 {
  margin: 0;
  color: #111827;
  font-weight: 700;
}

.brand p {
  margin: 3px 0 0;
  color: #6b7280;
  font-size: 12px;
}

.state-content {
  text-align: center;
}

.state-content h2 {
  margin: 24px 0 12px;
  color: #111827;
  font-size: 29px;
  font-weight: 750;
}

.state-content p {
  max-width: 390px;
  margin: 0 auto 32px;
  color: #6b7280;
  line-height: 1.7;
}

.loading-circle,
.success-circle,
.info-circle,
.error-circle {
  width: 88px;
  height: 88px;
  margin: 0 auto;
  border-radius: 50%;
  font-size: 41px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-circle {
  background: #eef2ff;
}

.success-circle {
  color: #16a34a;
  background: #dcfce7;
}

.info-circle {
  color: #4f46e5;
  background: #eef2ff;
}

.error-circle {
  color: #dc2626;
  background: #fef2f2;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 4px solid #c7d2fe;
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}

.primary-btn,
.secondary-btn {
  height: 52px;
  padding: 0 24px;
  border-radius: 13px;
  text-decoration: none;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
}

.primary-btn {
  color: white;
  background: #6366f1;
}

.primary-btn:hover {
  color: white;
  background: #4f46e5;
}

.secondary-btn {
  color: #4338ca;
  background: #eef2ff;
}

.secondary-btn:hover {
  color: #3730a3;
  background: #e0e7ff;
}

.side-panel {
  width: 395px;
  min-height: 570px;
  padding: 45px 39px;
  border-radius: 28px;
  color: white;
  background:
    radial-gradient(circle at 90% 12%, rgba(255, 255, 255, 0.2), transparent 26%),
    linear-gradient(145deg, #312e81, #4f46e5, #7c3aed);
  box-shadow: 0 27px 65px rgba(79, 70, 229, 0.22);
  display: flex;
  align-items: center;
}

.side-content > i {
  font-size: 46px;
}

.side-content h1 {
  margin: 23px 0 14px;
  font-size: 34px;
  font-weight: 750;
}

.side-content > p {
  margin: 0 0 38px;
  color: #e0e7ff;
  line-height: 1.7;
}

.feature {
  margin-top: 18px;
  color: #eef2ff;
  display: flex;
  align-items: center;
  gap: 11px;
}

.feature i {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  background: rgba(255, 255, 255, 0.14);
  display: flex;
  align-items: center;
  justify-content: center;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 940px) {
  .side-panel {
    display: none;
  }

  .verify-page {
    padding: 20px;
  }
}

@media (max-width: 576px) {
  .verify-card {
    padding: 27px 21px;
  }

  .state-content h2 {
    font-size: 25px;
  }
}
</style>