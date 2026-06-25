<template>
  <div class="exams-page">
    <div class="page-header">
      <div>
        <h2>Lịch thi</h2>
        <p>Theo dõi thời gian thi, địa điểm và các kỳ thi sắp diễn ra.</p>
      </div>

      <button class="primary-btn" @click="openAddModal">
        <i class="bi bi-plus-lg"></i>
        Thêm lịch thi
      </button>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon total">
            <i class="bi bi-calendar-event-fill"></i>
          </div>
          <div>
            <p>Tổng lịch thi</p>
            <h3>{{ exams.length }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon upcoming">
            <i class="bi bi-clock-history"></i>
          </div>
          <div>
            <p>Sắp diễn ra</p>
            <h3>{{ upcomingExams }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon soon">
            <i class="bi bi-exclamation-circle-fill"></i>
          </div>
          <div>
            <p>Trong 7 ngày tới</p>
            <h3>{{ examsInSevenDays }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon passed">
            <i class="bi bi-check-circle-fill"></i>
          </div>
          <div>
            <p>Đã qua</p>
            <h3>{{ pastExams }}</h3>
          </div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="toolbar">
        <div>
          <h5>Danh sách kỳ thi</h5>
          <p>Dữ liệu được lấy trực tiếp từ MariaDB.</p>
        </div>

        <div class="filters">
          <div class="search-box">
            <i class="bi bi-search"></i>
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="Tìm lịch thi..."
            />
          </div>

          <select v-model="selectedSubject">
            <option value="">Tất cả môn học</option>
            <option
              v-for="subject in subjects"
              :key="subject.id"
              :value="String(subject.id)"
            >
              {{ subject.name }}
            </option>
          </select>

          <select v-model="selectedTimeFilter">
            <option value="">Tất cả</option>
            <option value="UPCOMING">Sắp thi</option>
            <option value="PAST">Đã qua</option>
          </select>
        </div>
      </div>

      <div v-if="isLoading" class="loading-state">
        <span class="loading-spinner"></span>
        <p>Đang tải danh sách lịch thi...</p>
      </div>

      <div v-else-if="apiError" class="api-error-state">
        <div class="error-api-icon">
          <i class="bi bi-exclamation-circle"></i>
        </div>

        <h5>Không thể tải dữ liệu</h5>
        <p>{{ apiError }}</p>

        <button class="retry-btn" @click="loadInitialData">
          <i class="bi bi-arrow-clockwise"></i>
          Thử lại
        </button>
      </div>

      <div v-else-if="filteredExams.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="bi bi-calendar-x"></i>
        </div>

        <h5>Chưa có lịch thi phù hợp</h5>
        <p>Hãy thêm lịch thi mới hoặc thay đổi bộ lọc.</p>

        <button class="primary-btn" @click="openAddModal">
          <i class="bi bi-plus-lg"></i>
          Thêm lịch thi
        </button>
      </div>

      <div v-else class="exam-list">
        <div
          v-for="exam in filteredExams"
          :key="exam.id"
          class="exam-card"
          :class="{ passed: isPastExam(exam) }"
        >
          <div class="date-box">
            <strong>{{ getDay(exam.examDatetime) }}</strong>
            <span>{{ getMonth(exam.examDatetime) }}</span>
          </div>

          <div class="exam-main">
            <div class="exam-heading">
              <div>
                <div class="heading-row">
                  <h4>{{ exam.title }}</h4>

                  <span class="type-badge">
                    {{ exam.examType || 'Cuối kỳ' }}
                  </span>

                  <span
                    class="time-status"
                    :class="isPastExam(exam) ? 'past' : 'upcoming'"
                  >
                    {{ isPastExam(exam) ? 'Đã qua' : remainingText(exam) }}
                  </span>
                </div>

                <p class="subject-name">
                  <i class="bi bi-book"></i>
                  {{ exam.subjectName }}
                </p>
              </div>

              <div class="action-group">
                <button
                  class="action-btn edit"
                  title="Sửa lịch thi"
                  @click="openEditModal(exam)"
                >
                  <i class="bi bi-pencil-square"></i>
                </button>

                <button
                  class="action-btn delete"
                  title="Xóa lịch thi"
                  @click="confirmDelete(exam)"
                >
                  <i class="bi bi-trash3"></i>
                </button>
              </div>
            </div>

            <div class="exam-details">
              <div class="detail-item">
                <i class="bi bi-clock"></i>
                <div>
                  <small>Thời gian thi</small>
                  <p>{{ formatDateTime(exam.examDatetime) }}</p>
                </div>
              </div>

              <div class="detail-item">
                <i class="bi bi-geo-alt"></i>
                <div>
                  <small>Địa điểm</small>
                  <p>{{ exam.location || 'Chưa cập nhật' }}</p>
                </div>
              </div>

              <div class="detail-item">
                <i class="bi bi-calendar2-week"></i>
                <div>
                  <small>Trạng thái</small>
                  <p>{{ statusText(exam) }}</p>
                </div>
              </div>
            </div>

            <div v-if="exam.note" class="exam-note">
              <i class="bi bi-journal-text"></i>
              <span>{{ exam.note }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-header-custom">
          <div>
            <h4>{{ isEditing ? 'Cập nhật lịch thi' : 'Thêm lịch thi mới' }}</h4>
            <p>Nhập thông tin kỳ thi, thời gian và địa điểm thi.</p>
          </div>

          <button class="close-btn" @click="closeModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <form @submit.prevent="saveExam">
          <div class="form-group">
            <label>Tên kỳ thi <span>*</span></label>
            <input
              v-model.trim="form.title"
              type="text"
              placeholder="Ví dụ: Thi kết thúc môn Perl & Python"
              :class="{ invalid: errors.title }"
            />
            <small v-if="errors.title" class="error-text">
              {{ errors.title }}
            </small>
          </div>

          <div class="row g-3">
            <div class="col-md-7">
              <div class="form-group">
                <label>Môn học <span>*</span></label>
                <select
                  v-model="form.subjectId"
                  :class="{ invalid: errors.subjectId }"
                >
                  <option value="">Chọn môn học</option>
                  <option
                    v-for="subject in subjects"
                    :key="subject.id"
                    :value="String(subject.id)"
                  >
                    {{ subject.name }}
                  </option>
                </select>
                <small v-if="errors.subjectId" class="error-text">
                  {{ errors.subjectId }}
                </small>
              </div>
            </div>

            <div class="col-md-5">
              <div class="form-group">
                <label>Loại kỳ thi</label>
                <select v-model="form.examType">
                  <option value="Giữa kỳ">Giữa kỳ</option>
                  <option value="Cuối kỳ">Cuối kỳ</option>
                  <option value="Kiểm tra">Kiểm tra</option>
                  <option value="Thực hành">Thực hành</option>
                </select>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>Ngày giờ thi <span>*</span></label>
            <input
              v-model="form.examDatetime"
              type="datetime-local"
              :class="{ invalid: errors.examDatetime }"
            />
            <small v-if="errors.examDatetime" class="error-text">
              {{ errors.examDatetime }}
            </small>
          </div>

          <div class="form-group">
            <label>Địa điểm thi</label>
            <input
              v-model.trim="form.location"
              type="text"
              placeholder="Ví dụ: P.301"
            />
          </div>

          <div class="form-group">
            <label>Ghi chú ôn tập</label>
            <textarea
              v-model.trim="form.note"
              rows="3"
              placeholder="Ví dụ: Ôn Python, Perl, FastAPI và xử lý file..."
            ></textarea>
          </div>

          <div class="modal-footer-custom">
            <button type="button" class="cancel-btn" @click="closeModal">
              Hủy
            </button>

            <button type="submit" class="save-btn" :disabled="isSaving">
              <template v-if="!isSaving">
                <i class="bi bi-check-lg"></i>
                {{ isEditing ? 'Lưu thay đổi' : 'Thêm lịch thi' }}
              </template>

              <template v-else>
                <span class="button-spinner"></span>
                Đang lưu...
              </template>
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="examToDelete" class="modal-overlay" @click.self="examToDelete = null">
      <div class="delete-modal">
        <div class="delete-icon">
          <i class="bi bi-trash3"></i>
        </div>

        <h4>Xóa lịch thi?</h4>
        <p>
          Bạn có chắc muốn xóa kỳ thi
          <strong>{{ examToDelete.title }}</strong> không?
        </p>

        <div class="delete-actions">
          <button class="cancel-btn" @click="examToDelete = null">
            Hủy
          </button>

          <button
            class="confirm-delete-btn"
            :disabled="isDeleting"
            @click="deleteExam"
          >
            {{ isDeleting ? 'Đang xóa...' : 'Xóa lịch thi' }}
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="toast.message"
      class="toast-message"
      :class="toast.type"
    >
      <i
        class="bi"
        :class="toast.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'"
      ></i>
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const exams = ref([])
const subjects = ref([])

const searchKeyword = ref('')
const selectedSubject = ref('')
const selectedTimeFilter = ref('')

const isLoading = ref(false)
const isSaving = ref(false)
const isDeleting = ref(false)
const apiError = ref('')

const isModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const examToDelete = ref(null)

const toast = ref({
  message: '',
  type: 'success',
})

const form = ref({
  title: '',
  subjectId: '',
  examType: 'Cuối kỳ',
  examDatetime: '',
  location: '',
  note: '',
})

const emptyForm = () => ({
  title: '',
  subjectId: subjects.value[0]?.id ? String(subjects.value[0].id) : '',
  examType: 'Cuối kỳ',
  examDatetime: createDefaultExamDatetime(),
  location: '',
  note: '',
})

const errors = ref({
  title: '',
  subjectId: '',
  examDatetime: '',
})

const upcomingExams = computed(() => {
  return exams.value.filter((exam) => !isPastExam(exam)).length
})

const pastExams = computed(() => {
  return exams.value.filter((exam) => isPastExam(exam)).length
})

const examsInSevenDays = computed(() => {
  return exams.value.filter((exam) => {
    const days = getDaysRemaining(exam.examDatetime)
    return days >= 0 && days <= 7
  }).length
})

const filteredExams = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()

  return [...exams.value]
    .filter((exam) => {
      const matchesKeyword =
        exam.title.toLowerCase().includes(keyword) ||
        exam.subjectName.toLowerCase().includes(keyword) ||
        (exam.location || '').toLowerCase().includes(keyword) ||
        (exam.note || '').toLowerCase().includes(keyword)

      const matchesSubject =
        !selectedSubject.value ||
        String(exam.subjectId) === String(selectedSubject.value)

      const matchesTime =
        !selectedTimeFilter.value ||
        (selectedTimeFilter.value === 'UPCOMING' && !isPastExam(exam)) ||
        (selectedTimeFilter.value === 'PAST' && isPastExam(exam))

      return matchesKeyword && matchesSubject && matchesTime
    })
    .sort(
      (first, second) =>
        new Date(first.examDatetime).getTime() -
        new Date(second.examDatetime).getTime(),
    )
})

const mapSubjectFromApi = (subject) => ({
  id: subject.id,
  name: subject.name,
})

const mapExamFromApi = (exam) => ({
  id: exam.id,
  subjectId: exam.subject_id,
  subjectName: exam.subject_name,
  title: exam.title,
  examType: exam.exam_type || 'Cuối kỳ',
  examDatetime: exam.exam_datetime,
  location: exam.location || '',
  note: exam.note || '',
  daysRemaining: exam.days_remaining,
  timeStatus: exam.time_status,
  createdAt: exam.created_at,
  updatedAt: exam.updated_at,
})

const showToast = (message, type = 'success') => {
  toast.value = { message, type }

  setTimeout(() => {
    toast.value.message = ''
  }, 2800)
}

const handleApiError = (error, fallbackMessage) => {
  if (error.response?.status === 401) {
    router.push('/dang-nhap')
    return 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.'
  }

  return error.response?.data?.detail || fallbackMessage
}

const fetchSubjects = async () => {
  const response = await api.get('/subjects')
  subjects.value = response.data.map(mapSubjectFromApi)
}

const fetchExams = async () => {
  const response = await api.get('/exams')
  exams.value = response.data.map(mapExamFromApi)
}

const loadInitialData = async () => {
  isLoading.value = true
  apiError.value = ''

  try {
    await Promise.all([fetchSubjects(), fetchExams()])
  } catch (error) {
    apiError.value = handleApiError(
      error,
      'Không thể kết nối hệ thống. Vui lòng thử lại.',
    )
  } finally {
    isLoading.value = false
  }
}

const resetErrors = () => {
  errors.value = {
    title: '',
    subjectId: '',
    examDatetime: '',
  }
}

const openAddModal = () => {
  isEditing.value = false
  editingId.value = null
  form.value = emptyForm()
  resetErrors()
  isModalOpen.value = true
}

const openEditModal = (exam) => {
  isEditing.value = true
  editingId.value = exam.id

  form.value = {
    title: exam.title,
    subjectId: String(exam.subjectId),
    examType: exam.examType || 'Cuối kỳ',
    examDatetime: toDatetimeLocal(exam.examDatetime),
    location: exam.location || '',
    note: exam.note || '',
  }

  resetErrors()
  isModalOpen.value = true
}

const closeModal = () => {
  if (isSaving.value) return

  isModalOpen.value = false
  resetErrors()
}

const validateForm = () => {
  resetErrors()
  let valid = true

  if (!form.value.title.trim()) {
    errors.value.title = 'Vui lòng nhập tên kỳ thi.'
    valid = false
  }

  if (!form.value.subjectId) {
    errors.value.subjectId = 'Vui lòng chọn môn học.'
    valid = false
  }

  if (!form.value.examDatetime) {
    errors.value.examDatetime = 'Vui lòng chọn ngày giờ thi.'
    valid = false
  }

  return valid
}

const buildPayload = () => ({
  subject_id: Number(form.value.subjectId),
  title: form.value.title.trim(),
  exam_type: form.value.examType || 'Cuối kỳ',
  exam_datetime: form.value.examDatetime,
  location: form.value.location.trim() || null,
  note: form.value.note.trim() || null,
})

const saveExam = async () => {
  if (!validateForm()) return

  isSaving.value = true

  try {
    if (isEditing.value) {
      const response = await api.put(`/exams/${editingId.value}`, buildPayload())
      const updatedExam = mapExamFromApi(response.data)

      const index = exams.value.findIndex((exam) => exam.id === editingId.value)

      if (index !== -1) {
        exams.value[index] = updatedExam
      }

      showToast('Cập nhật lịch thi thành công.')
    } else {
      const response = await api.post('/exams', buildPayload())
      exams.value.unshift(mapExamFromApi(response.data))
      showToast('Thêm lịch thi thành công.')
    }

    closeModal()
  } catch (error) {
    showToast(
      handleApiError(error, 'Không thể lưu lịch thi. Vui lòng thử lại.'),
      'error',
    )
  } finally {
    isSaving.value = false
  }
}

const confirmDelete = (exam) => {
  examToDelete.value = exam
}

const deleteExam = async () => {
  if (!examToDelete.value) return

  isDeleting.value = true

  try {
    await api.delete(`/exams/${examToDelete.value.id}`)

    exams.value = exams.value.filter(
      (exam) => exam.id !== examToDelete.value.id,
    )

    examToDelete.value = null
    showToast('Xóa lịch thi thành công.')
  } catch (error) {
    showToast(
      handleApiError(error, 'Không thể xóa lịch thi. Vui lòng thử lại.'),
      'error',
    )
  } finally {
    isDeleting.value = false
  }
}

function toDatetimeLocal(value) {
  if (!value) return ''

  const date = new Date(value)
  const offset = date.getTimezoneOffset()
  const localDate = new Date(date.getTime() - offset * 60 * 1000)

  return localDate.toISOString().slice(0, 16)
}

function createDefaultExamDatetime() {
  const date = new Date()
  date.setDate(date.getDate() + 7)
  date.setHours(8, 0, 0, 0)

  return toDatetimeLocal(date)
}

const formatDateTime = (value) => {
  if (!value) return '---'

  return new Date(value).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

const getDay = (value) => {
  return new Date(value).toLocaleDateString('vi-VN', {
    day: '2-digit',
  })
}

const getMonth = (value) => {
  const month = new Date(value).getMonth() + 1
  return `TH${month}`
}

const getDaysRemaining = (value) => {
  const milliseconds = new Date(value).getTime() - new Date().getTime()
  return Math.ceil(milliseconds / (1000 * 60 * 60 * 24))
}

const isPastExam = (exam) => {
  return new Date(exam.examDatetime).getTime() < new Date().getTime()
}

const remainingText = (exam) => {
  const days = getDaysRemaining(exam.examDatetime)

  if (days <= 0) {
    return 'Thi hôm nay'
  }

  if (days === 1) {
    return 'Còn 1 ngày'
  }

  return `Còn ${days} ngày`
}

const statusText = (exam) => {
  if (isPastExam(exam)) return 'Đã qua'

  const days = getDaysRemaining(exam.examDatetime)

  if (days <= 0) return 'Thi hôm nay'
  if (days <= 7) return 'Sắp diễn ra'

  return 'Đang chờ'
}

onMounted(() => {
  loadInitialData()
})
</script>

<style scoped>
.exams-page {
  position: relative;
}

.page-header {
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-header h2 {
  margin: 0 0 7px;
  color: var(--sm-text);
  font-size: 27px;
  font-weight: 700;
}

.page-header p {
  margin: 0;
  color: var(--sm-text-soft);
}

.primary-btn {
  height: 47px;
  padding: 0 20px;
  border: none;
  border-radius: 12px;
  color: white;
  background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
  box-shadow: 0 10px 22px rgba(185, 130, 76, 0.2);
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 9px;
}

.primary-btn:hover {
  background: linear-gradient(135deg, var(--sm-primary-dark), var(--sm-primary));
  transform: translateY(-1px);
}

.summary-card {
  height: 110px;
  padding: 22px;
  border: 1px solid var(--sm-border);
  border-radius: 18px;
  background: var(--sm-card);
  box-shadow: var(--sm-shadow-sm);
  display: flex;
  align-items: center;
  gap: 18px;
}

.summary-icon {
  width: 56px;
  height: 56px;
  border-radius: 15px;
  font-size: 25px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.summary-icon.total {
  color: var(--sm-primary);
  background: var(--sm-primary-soft);
}

.summary-icon.upcoming {
  color: var(--sm-primary-dark);
  background: var(--sm-accent-soft);
}

.summary-icon.soon {
  color: var(--sm-warning);
  background: var(--sm-warning-bg);
}

.summary-icon.passed {
  color: var(--sm-success);
  background: var(--sm-success-bg);
}

.summary-card p {
  margin: 0 0 6px;
  color: var(--sm-text-soft);
  font-size: 14px;
}

.summary-card h3 {
  margin: 0;
  color: var(--sm-text);
  font-size: 28px;
  font-weight: 700;
}

.content-card {
  padding: 24px;
  border: 1px solid var(--sm-border);
  border-radius: 19px;
  background: var(--sm-card);
  box-shadow: var(--sm-shadow-sm);
}

.toolbar {
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

.toolbar h5 {
  margin: 0 0 5px;
  color: var(--sm-text);
  font-weight: 700;
}

.toolbar p {
  margin: 0;
  color: var(--sm-text-soft);
  font-size: 14px;
}

.filters {
  display: flex;
  gap: 10px;
}

.search-box {
  width: 245px;
  height: 44px;
  padding: 0 14px;
  border: 1px solid var(--sm-border);
  border-radius: 11px;
  color: var(--sm-text-soft);
  background: #fffdfa;
  display: flex;
  align-items: center;
  gap: 9px;
}

.search-box:focus-within {
  border-color: #d8b992;
  box-shadow: 0 0 0 3px var(--sm-primary-soft);
}

.search-box input {
  width: 100%;
  border: none;
  outline: none;
  color: var(--sm-text);
  background: transparent;
}

.filters select {
  height: 44px;
  min-width: 145px;
  padding: 0 12px;
  border: 1px solid var(--sm-border);
  border-radius: 11px;
  color: var(--sm-text);
  background: #fffdfa;
}

.loading-state,
.api-error-state,
.empty-state {
  padding: 55px 20px;
  text-align: center;
}

.loading-spinner {
  width: 39px;
  height: 39px;
  margin: 0 auto;
  border: 4px solid #ead8c3;
  border-top-color: var(--sm-primary);
  border-radius: 50%;
  display: block;
  animation: spin 0.75s linear infinite;
}

.loading-state p,
.api-error-state p,
.empty-state p {
  margin-top: 16px;
  color: var(--sm-text-soft);
}

.empty-icon,
.error-api-icon {
  width: 68px;
  height: 68px;
  margin: 0 auto 18px;
  border-radius: 50%;
  font-size: 31px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.empty-icon {
  color: var(--sm-primary);
  background: var(--sm-primary-soft);
}

.error-api-icon {
  color: var(--sm-danger);
  background: var(--sm-danger-bg);
}

.retry-btn {
  height: 45px;
  padding: 0 18px;
  border: 1px solid var(--sm-border-strong);
  border-radius: 11px;
  color: var(--sm-primary-dark);
  background: var(--sm-primary-soft);
  font-weight: 600;
}

.retry-btn i {
  margin-right: 7px;
}

.exam-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.exam-card {
  padding: 20px;
  border: 1px solid var(--sm-border);
  border-radius: 17px;
  background: #fffdfa;
  display: flex;
  gap: 18px;
  transition: 0.2s;
}

.exam-card:hover {
  border-color: var(--sm-border-strong);
  box-shadow: var(--sm-shadow-sm);
}

.exam-card.passed {
  opacity: 0.72;
}

.date-box {
  width: 67px;
  height: 72px;
  flex-shrink: 0;
  border-radius: 16px;
  color: var(--sm-primary-dark);
  background: var(--sm-primary-soft);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  line-height: 23px;
}

.date-box strong {
  font-size: 27px;
}

.date-box span {
  color: var(--sm-primary);
  font-size: 12px;
  font-weight: 700;
}

.exam-main {
  flex: 1;
}

.exam-heading {
  display: flex;
  justify-content: space-between;
  gap: 15px;
}

.heading-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 9px;
}

.heading-row h4 {
  margin: 0;
  color: var(--sm-text);
  font-size: 18px;
  font-weight: 700;
}

.type-badge {
  padding: 5px 10px;
  border-radius: 20px;
  color: var(--sm-primary-dark);
  background: var(--sm-primary-soft);
  font-size: 12px;
  font-weight: 600;
}

.time-status {
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.time-status.upcoming {
  color: var(--sm-warning);
  background: var(--sm-warning-bg);
}

.time-status.past {
  color: var(--sm-text-soft);
  background: #f4ede5;
}

.subject-name {
  margin: 8px 0 0;
  color: var(--sm-text-soft);
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 7px;
}

.action-group {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 37px;
  height: 37px;
  border: none;
  border-radius: 9px;
}

.action-btn.edit {
  color: var(--sm-warning);
  background: var(--sm-warning-bg);
}

.action-btn.delete {
  color: var(--sm-danger);
  background: var(--sm-danger-bg);
}

.exam-details {
  margin-top: 19px;
  display: flex;
  flex-wrap: wrap;
  gap: 35px;
}

.detail-item {
  min-width: 185px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.detail-item > i {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  color: var(--sm-primary);
  background: var(--sm-primary-soft);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-item small {
  display: block;
  color: var(--sm-text-soft);
  margin-bottom: 3px;
}

.detail-item p {
  margin: 0;
  color: var(--sm-text);
  font-size: 14px;
  font-weight: 500;
}

.exam-note {
  margin-top: 18px;
  padding: 11px 14px;
  border-radius: 10px;
  color: var(--sm-text-soft);
  background: var(--sm-accent-soft);
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 14px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 300;
  padding: 22px;
  background: rgba(48, 40, 33, 0.48);
  backdrop-filter: blur(3px);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-card {
  width: 680px;
  max-width: 100%;
  max-height: 94vh;
  overflow-y: auto;
  padding: 27px;
  border: 1px solid var(--sm-border);
  border-radius: 20px;
  background: var(--sm-card);
  box-shadow: var(--sm-shadow-md);
}

.modal-header-custom {
  margin-bottom: 23px;
  display: flex;
  justify-content: space-between;
}

.modal-header-custom h4 {
  margin: 0 0 6px;
  color: var(--sm-text);
  font-weight: 700;
}

.modal-header-custom p {
  margin: 0;
  color: var(--sm-text-soft);
  font-size: 14px;
}

.close-btn {
  width: 38px;
  height: 38px;
  border: none;
  border-radius: 9px;
  color: var(--sm-text);
  background: var(--sm-accent-soft);
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--sm-text);
  font-size: 14px;
  font-weight: 600;
}

.form-group label span {
  color: var(--sm-danger);
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px 13px;
  border: 1px solid var(--sm-border);
  border-radius: 11px;
  outline: none;
  color: var(--sm-text);
  background: #fffdfa;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #d8b992;
  box-shadow: 0 0 0 3px var(--sm-primary-soft);
}

.form-group .invalid {
  border-color: var(--sm-danger);
}

.error-text {
  display: block;
  margin-top: 6px;
  color: var(--sm-danger);
  font-size: 12px;
}

.modal-footer-custom {
  display: flex;
  justify-content: flex-end;
  gap: 11px;
}

.cancel-btn,
.save-btn,
.confirm-delete-btn {
  height: 45px;
  padding: 0 19px;
  border-radius: 11px;
  font-weight: 600;
}

.cancel-btn {
  border: 1px solid var(--sm-border);
  color: var(--sm-text);
  background: #fffdfa;
}

.save-btn {
  border: none;
  color: white;
  background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
  display: flex;
  align-items: center;
  gap: 7px;
}

.save-btn:disabled,
.confirm-delete-btn:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.button-spinner {
  width: 17px;
  height: 17px;
  border: 2px solid rgba(255, 255, 255, 0.45);
  border-top-color: white;
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.7s linear infinite;
}

.delete-modal {
  width: 420px;
  max-width: 100%;
  padding: 31px;
  border: 1px solid var(--sm-border);
  border-radius: 20px;
  background: var(--sm-card);
  box-shadow: var(--sm-shadow-md);
  text-align: center;
}

.delete-icon {
  width: 62px;
  height: 62px;
  margin: 0 auto 18px;
  border-radius: 50%;
  color: var(--sm-danger);
  background: var(--sm-danger-bg);
  font-size: 27px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.delete-modal h4 {
  color: var(--sm-text);
  font-weight: 700;
}

.delete-modal p {
  margin: 12px 0 25px;
  color: var(--sm-text-soft);
}

.delete-actions {
  display: flex;
  justify-content: center;
  gap: 11px;
}

.confirm-delete-btn {
  border: none;
  color: white;
  background: var(--sm-danger);
}

.toast-message {
  position: fixed;
  z-index: 500;
  top: 94px;
  right: 28px;
  padding: 14px 18px;
  border-radius: 11px;
  color: white;
  box-shadow: 0 10px 30px rgba(67, 45, 30, 0.16);
  display: flex;
  align-items: center;
  gap: 9px;
}

.toast-message.success {
  background: var(--sm-success);
}

.toast-message.error {
  background: var(--sm-danger);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1200px) {
  .toolbar {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .page-header,
  .filters,
  .exam-heading {
    flex-direction: column;
    align-items: flex-start;
  }

  .filters,
  .search-box,
  .filters select {
    width: 100%;
  }

  .exam-card {
    flex-direction: column;
  }

  .exam-details {
    gap: 18px;
  }
}
</style>