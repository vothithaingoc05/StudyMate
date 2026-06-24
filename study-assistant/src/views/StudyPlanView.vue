<template>
  <div class="study-plan-page">
    <div class="page-header">
      <div>
        <h2>Kế hoạch ôn tập</h2>
        <p>Lập lịch học theo ngày và theo dõi tiến độ ôn tập của bạn.</p>
      </div>

      <button class="primary-btn" @click="openAddModal">
        <i class="bi bi-plus-lg"></i>
        Tạo kế hoạch học
      </button>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon total">
            <i class="bi bi-calendar-check-fill"></i>
          </div>

          <div>
            <p>Tổng kế hoạch</p>
            <h3>{{ plans.length }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon today">
            <i class="bi bi-calendar-day-fill"></i>
          </div>

          <div>
            <p>Lịch học hôm nay</p>
            <h3>{{ todayPlans }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon pending">
            <i class="bi bi-hourglass-split"></i>
          </div>

          <div>
            <p>Chưa hoàn thành</p>
            <h3>{{ unfinishedPlans }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon done">
            <i class="bi bi-stopwatch-fill"></i>
          </div>

          <div>
            <p>Tổng thời gian học</p>
            <h3>{{ totalStudyHours }}</h3>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-xl-8">
        <div class="content-card">
          <div>
            <h5>Lịch ôn tập của bạn</h5>
          </div>
          <div class="toolbar">
            <div class="filters">
              <div class="search-box">
                <i class="bi bi-search"></i>
                <input v-model="searchKeyword" type="text" placeholder="Tìm kế hoạch..." />
              </div>

              <select v-model="selectedSubject">
                <option value="">Tất cả môn</option>
                <option v-for="subject in subjects" :key="subject.id" :value="String(subject.id)">
                  {{ subject.name }}
                </option>
              </select>

              <select v-model="selectedStatus">
                <option value="">Tất cả trạng thái</option>
                <option value="CHUA_THUC_HIEN">Chưa thực hiện</option>
                <option value="DANG_THUC_HIEN">Đang thực hiện</option>
                <option value="DA_HOAN_THANH">Đã hoàn thành</option>
              </select>
            </div>
          </div>

          <div class="date-filter-row">
            <button v-for="filter in dateFilters" :key="filter.value" class="date-filter-btn"
              :class="{ active: selectedDateFilter === filter.value }" @click="selectedDateFilter = filter.value">
              {{ filter.label }}
            </button>
          </div>

          <div v-if="isLoading" class="loading-state">
            <span class="loading-spinner"></span>
            <p>Đang tải kế hoạch ôn tập...</p>
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

          <div v-else-if="filteredPlans.length === 0" class="empty-state">
            <div class="empty-icon">
              <i class="bi bi-calendar2-x"></i>
            </div>

            <h5>Chưa có kế hoạch ôn tập</h5>
            <p>Hãy tạo lịch học mới để bắt đầu theo dõi tiến độ.</p>

            <button class="primary-btn" @click="openAddModal">
              <i class="bi bi-plus-lg"></i>
              Tạo kế hoạch học
            </button>
          </div>

          <div v-else class="plan-list">
            <div v-for="plan in filteredPlans" :key="plan.id" class="plan-card" :class="{
              completed: plan.status === 'DA_HOAN_THANH',
              today: isToday(plan.studyDate),
            }">
              <div class="plan-time">
                <strong>{{ formatTime(plan.startTime) }}</strong>
                <span>{{ plan.durationMinutes }} phút</span>
              </div>

              <div class="plan-content">
                <div class="plan-heading">
                  <div>
                    <div class="heading-title">
                      <h4>{{ plan.title }}</h4>

                      <span v-if="isToday(plan.studyDate)" class="today-badge">
                        Hôm nay
                      </span>
                    </div>

                    <p class="plan-date">
                      <i class="bi bi-calendar3"></i>
                      {{ formatDate(plan.studyDate) }}
                    </p>
                  </div>

                  <div class="action-group">
                    <button class="action-btn edit" title="Sửa kế hoạch" @click="openEditModal(plan)">
                      <i class="bi bi-pencil-square"></i>
                    </button>

                    <button class="action-btn delete" title="Xóa kế hoạch" @click="confirmDelete(plan)">
                      <i class="bi bi-trash3"></i>
                    </button>
                  </div>
                </div>

                <div class="plan-meta">
                  <span class="subject-badge">
                    <i class="bi bi-book"></i>
                    {{ plan.subjectName }}
                  </span>

                  <span v-if="plan.taskTitle" class="task-badge">
                    <i class="bi bi-check2-square"></i>
                    {{ plan.taskTitle }}
                  </span>
                </div>

                <p class="plan-description">
                  {{ plan.content || 'Chưa có nội dung ôn tập cụ thể.' }}
                </p>

                <div class="plan-footer">
                  <select class="status-select" :class="plan.status.toLowerCase()" :value="plan.status"
                    @change="changeStatus(plan, $event.target.value)">
                    <option value="CHUA_THUC_HIEN">Chưa thực hiện</option>
                    <option value="DANG_THUC_HIEN">Đang thực hiện</option>
                    <option value="DA_HOAN_THANH">Đã hoàn thành</option>
                  </select>

                  <div class="duration-note">
                    <i class="bi bi-clock"></i>
                    {{ getDurationText(plan.durationMinutes) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar kế hoạch -->
      <div class="col-xl-4">
        <div class="side-card mb-4">
          <div class="side-header">
            <h5>Buổi học sắp tới</h5>
            <span>{{ upcomingPlans.length }} lịch</span>
          </div>

          <div v-if="upcomingPlans.length === 0" class="small-empty">
            Chưa có lịch học sắp tới.
          </div>

          <div v-for="plan in upcomingPlans.slice(0, 4)" :key="plan.id" class="upcoming-item">
            <div class="upcoming-date">
              <strong>{{ getDay(plan.studyDate) }}</strong>
              <small>{{ getMonth(plan.studyDate) }}</small>
            </div>

            <div class="upcoming-content">
              <p>{{ plan.title }}</p>
              <small>
                {{ formatTime(plan.startTime) }} · {{ plan.subjectName }}
              </small>
            </div>
          </div>
        </div>

        <div class="progress-card">
          <div class="progress-icon">
            <i class="bi bi-graph-up-arrow"></i>
          </div>

          <h5>Tiến độ ôn tập</h5>

          <div class="progress-value">
            <strong>{{ completionPercent }}%</strong>
            <span>đã hoàn thành</span>
          </div>

          <div class="custom-progress">
            <div class="custom-progress-bar" :style="{ width: `${completionPercent}%` }"></div>
          </div>

          <p>
            Bạn đã hoàn thành
            <strong>{{ completedPlans }}/{{ plans.length }}</strong>
            kế hoạch học tập.
          </p>
        </div>
      </div>
    </div>

    <!-- Modal Add / Edit -->
    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-header-custom">
          <div>
            <h4>
              {{ isEditing ? 'Cập nhật kế hoạch học' : 'Tạo kế hoạch học mới' }}
            </h4>
            <p>Thiết lập thời gian và nội dung cần ôn tập.</p>
          </div>

          <button class="close-btn" @click="closeModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <form @submit.prevent="savePlan">
          <div class="form-group">
            <label>Tiêu đề kế hoạch <span>*</span></label>
            <input v-model.trim="form.title" type="text" placeholder="Ví dụ: Ôn Python buổi tối"
              :class="{ invalid: errors.title }" />
            <small v-if="errors.title" class="error-text">
              {{ errors.title }}
            </small>
          </div>

          <div class="row g-3">
            <div class="col-md-6">
              <div class="form-group">
                <label>Môn học <span>*</span></label>
                <select v-model="form.subjectId" :class="{ invalid: errors.subjectId }" @change="form.taskId = ''">
                  <option value="">Chọn môn học</option>
                  <option v-for="subject in subjects" :key="subject.id" :value="String(subject.id)">
                    {{ subject.name }}
                  </option>
                </select>
                <small v-if="errors.subjectId" class="error-text">
                  {{ errors.subjectId }}
                </small>
              </div>
            </div>

            <div class="col-md-6">
              <div class="form-group">
                <label>Bài tập liên quan</label>
                <select v-model="form.taskId">
                  <option value="">Không liên kết bài tập</option>
                  <option v-for="task in availableTasks" :key="task.id" :value="String(task.id)">
                    {{ task.title }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <div class="row g-3">
            <div class="col-md-5">
              <div class="form-group">
                <label>Ngày học <span>*</span></label>
                <input v-model="form.studyDate" type="date" :class="{ invalid: errors.studyDate }" />
                <small v-if="errors.studyDate" class="error-text">
                  {{ errors.studyDate }}
                </small>
              </div>
            </div>

            <div class="col-md-3">
              <div class="form-group">
                <label>Giờ bắt đầu</label>
                <input v-model="form.startTime" type="time" />
              </div>
            </div>

            <div class="col-md-4">
              <div class="form-group">
                <label>Thời lượng</label>
                <select v-model.number="form.durationMinutes">
                  <option :value="30">30 phút</option>
                  <option :value="45">45 phút</option>
                  <option :value="60">1 giờ</option>
                  <option :value="90">1 giờ 30 phút</option>
                  <option :value="120">2 giờ</option>
                  <option :value="180">3 giờ</option>
                </select>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label>Nội dung cần ôn</label>
            <textarea v-model.trim="form.content" rows="4"
              placeholder="Ví dụ: Ôn vòng lặp for, while và làm bài tập minh họa..."></textarea>
          </div>

          <div class="form-group">
            <label>Trạng thái</label>
            <select v-model="form.status">
              <option value="CHUA_THUC_HIEN">Chưa thực hiện</option>
              <option value="DANG_THUC_HIEN">Đang thực hiện</option>
              <option value="DA_HOAN_THANH">Đã hoàn thành</option>
            </select>
          </div>

          <div class="plan-preview">
            <div class="preview-icon">
              <i class="bi bi-calendar-heart"></i>
            </div>

            <div>
              <p>Lịch học dự kiến</p>
              <strong>
                {{ form.studyDate ? formatDate(form.studyDate) : 'Chưa chọn ngày' }}
                · {{ formatTime(form.startTime) }}
                · {{ getDurationText(form.durationMinutes) }}
              </strong>
            </div>
          </div>

          <div class="modal-footer-custom">
            <button type="button" class="cancel-btn" @click="closeModal">
              Hủy
            </button>

            <button type="submit" class="save-btn" :disabled="isSaving">
              <template v-if="!isSaving">
                <i class="bi bi-check-lg"></i>
                {{ isEditing ? 'Lưu thay đổi' : 'Tạo kế hoạch' }}
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

    <!-- Delete modal -->
    <div v-if="planToDelete" class="modal-overlay" @click.self="planToDelete = null">
      <div class="delete-modal">
        <div class="delete-icon">
          <i class="bi bi-trash3"></i>
        </div>

        <h4>Xóa kế hoạch học?</h4>
        <p>
          Bạn có chắc muốn xóa kế hoạch
          <strong>{{ planToDelete.title }}</strong> không?
        </p>

        <div class="delete-actions">
          <button class="cancel-btn" @click="planToDelete = null">
            Hủy
          </button>

          <button class="confirm-delete-btn" :disabled="isDeleting" @click="deletePlan">
            {{ isDeleting ? 'Đang xóa...' : 'Xóa kế hoạch' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="toast.message" class="toast-message" :class="toast.type">
      <i class="bi" :class="toast.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'"></i>
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const plans = ref([])
const subjects = ref([])
const tasks = ref([])

const searchKeyword = ref('')
const selectedSubject = ref('')
const selectedStatus = ref('')
const selectedDateFilter = ref('ALL')

const isLoading = ref(false)
const isSaving = ref(false)
const isDeleting = ref(false)
const apiError = ref('')

const isModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const planToDelete = ref(null)

const toast = ref({
  message: '',
  type: 'success',
})

const dateFilters = [
  { label: 'Tất cả', value: 'ALL' },
  { label: 'Hôm nay', value: 'TODAY' },
  { label: 'Sắp tới', value: 'UPCOMING' },
  { label: 'Đã qua', value: 'PAST' },
]

const form = ref({
  subjectId: '',
  taskId: '',
  title: '',
  content: '',
  studyDate: '',
  startTime: '19:00',
  durationMinutes: 60,
  status: 'CHUA_THUC_HIEN',
})

const errors = ref({
  title: '',
  subjectId: '',
  studyDate: '',
})

const completedPlans = computed(() => {
  return plans.value.filter((plan) => plan.status === 'DA_HOAN_THANH').length
})

const unfinishedPlans = computed(() => {
  return plans.value.filter((plan) => plan.status !== 'DA_HOAN_THANH').length
})

const todayPlans = computed(() => {
  return plans.value.filter((plan) => isToday(plan.studyDate)).length
})

const totalStudyHours = computed(() => {
  const minutes = plans.value.reduce(
    (total, plan) => total + Number(plan.durationMinutes || 0),
    0,
  )

  const hours = minutes / 60
  return Number.isInteger(hours) ? `${hours}h` : `${hours.toFixed(1)}h`
})

const completionPercent = computed(() => {
  if (plans.value.length === 0) return 0
  return Math.round((completedPlans.value / plans.value.length) * 100)
})

const upcomingPlans = computed(() => {
  return [...plans.value]
    .filter(
      (plan) =>
        plan.status !== 'DA_HOAN_THANH' &&
        new Date(`${plan.studyDate}T23:59:59`).getTime() >= new Date().getTime(),
    )
    .sort((first, second) => getPlanTimestamp(first) - getPlanTimestamp(second))
})

const availableTasks = computed(() => {
  if (!form.value.subjectId) return []

  return tasks.value.filter(
    (task) => String(task.subjectId) === String(form.value.subjectId),
  )
})

const filteredPlans = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()

  return [...plans.value]
    .filter((plan) => {
      const matchesKeyword =
        plan.title.toLowerCase().includes(keyword) ||
        (plan.content || '').toLowerCase().includes(keyword) ||
        plan.subjectName.toLowerCase().includes(keyword) ||
        (plan.taskTitle || '').toLowerCase().includes(keyword)

      const matchesSubject =
        !selectedSubject.value ||
        String(plan.subjectId) === String(selectedSubject.value)

      const matchesStatus =
        !selectedStatus.value || plan.status === selectedStatus.value

      let matchesDate = true

      if (selectedDateFilter.value === 'TODAY') {
        matchesDate = isToday(plan.studyDate)
      }

      if (selectedDateFilter.value === 'UPCOMING') {
        matchesDate =
          new Date(`${plan.studyDate}T23:59:59`).getTime() >=
          new Date().getTime() && !isToday(plan.studyDate)
      }

      if (selectedDateFilter.value === 'PAST') {
        matchesDate =
          new Date(`${plan.studyDate}T23:59:59`).getTime() <
          new Date().getTime()
      }

      return matchesKeyword && matchesSubject && matchesStatus && matchesDate
    })
    .sort((first, second) => getPlanTimestamp(first) - getPlanTimestamp(second))
})

const mapSubjectFromApi = (subject) => ({
  id: subject.id,
  name: subject.name,
})

const mapTaskFromApi = (task) => ({
  id: task.id,
  subjectId: task.subject_id,
  title: task.title,
})

const mapPlanFromApi = (plan) => ({
  id: plan.id,
  subjectId: plan.subject_id,
  subjectName: plan.subject_name,
  taskId: plan.task_id ? String(plan.task_id) : '',
  taskTitle: plan.task_title || '',
  title: plan.title,
  content: plan.content || '',
  studyDate: plan.study_date,
  startTime: plan.start_time ? String(plan.start_time).slice(0, 5) : '',
  durationMinutes: plan.duration_minutes,
  status: plan.status,
  completedAt: plan.completed_at,
  createdAt: plan.created_at,
  updatedAt: plan.updated_at,
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

const fetchTasks = async () => {
  const response = await api.get('/tasks')
  tasks.value = response.data.map(mapTaskFromApi)
}

const fetchPlans = async () => {
  const response = await api.get('/study-plans')
  plans.value = response.data.map(mapPlanFromApi)
}

const loadInitialData = async () => {
  isLoading.value = true
  apiError.value = ''

  try {
    await Promise.all([fetchSubjects(), fetchTasks(), fetchPlans()])
  } catch (error) {
    apiError.value = handleApiError(
      error,
      'Không thể kết nối hệ thống. Vui lòng thử lại.',
    )
  } finally {
    isLoading.value = false
  }
}

const emptyForm = () => ({
  subjectId: subjects.value[0]?.id ? String(subjects.value[0].id) : '',
  taskId: '',
  title: '',
  content: '',
  studyDate: toInputDate(new Date()),
  startTime: '19:00',
  durationMinutes: 60,
  status: 'CHUA_THUC_HIEN',
})

const resetErrors = () => {
  errors.value = {
    title: '',
    subjectId: '',
    studyDate: '',
  }
}

const openAddModal = () => {
  isEditing.value = false
  editingId.value = null
  form.value = emptyForm()
  resetErrors()
  isModalOpen.value = true
}

const openEditModal = (plan) => {
  isEditing.value = true
  editingId.value = plan.id

  form.value = {
    subjectId: String(plan.subjectId),
    taskId: plan.taskId ? String(plan.taskId) : '',
    title: plan.title,
    content: plan.content,
    studyDate: plan.studyDate,
    startTime: plan.startTime || '19:00',
    durationMinutes: plan.durationMinutes,
    status: plan.status,
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
    errors.value.title = 'Vui lòng nhập tiêu đề kế hoạch.'
    valid = false
  }

  if (!form.value.subjectId) {
    errors.value.subjectId = 'Vui lòng chọn môn học.'
    valid = false
  }

  if (!form.value.studyDate) {
    errors.value.studyDate = 'Vui lòng chọn ngày học.'
    valid = false
  }

  return valid
}

const buildPayload = () => ({
  subject_id: Number(form.value.subjectId),
  task_id: form.value.taskId ? Number(form.value.taskId) : null,
  title: form.value.title.trim(),
  content: form.value.content.trim() || null,
  study_date: form.value.studyDate,
  start_time: form.value.startTime ? `${form.value.startTime}:00` : null,
  duration_minutes: Number(form.value.durationMinutes),
  status: form.value.status,
})

const savePlan = async () => {
  if (!validateForm()) return

  isSaving.value = true

  try {
    if (isEditing.value) {
      const response = await api.put(
        `/study-plans/${editingId.value}`,
        buildPayload(),
      )

      const updatedPlan = mapPlanFromApi(response.data)
      const index = plans.value.findIndex((plan) => plan.id === editingId.value)

      if (index !== -1) {
        plans.value[index] = updatedPlan
      }

      showToast('Cập nhật kế hoạch thành công.')
    } else {
      const response = await api.post('/study-plans', buildPayload())
      plans.value.unshift(mapPlanFromApi(response.data))
      showToast('Tạo kế hoạch học thành công.')
    }

    closeModal()
  } catch (error) {
    showToast(
      handleApiError(error, 'Không thể lưu kế hoạch học. Vui lòng thử lại.'),
      'error',
    )
  } finally {
    isSaving.value = false
  }
}

const changeStatus = async (plan, status) => {
  try {
    const response = await api.patch(`/study-plans/${plan.id}/status`, {
      status,
    })

    const updatedPlan = mapPlanFromApi(response.data)
    const index = plans.value.findIndex((item) => item.id === plan.id)

    if (index !== -1) {
      plans.value[index] = updatedPlan
    }

    showToast('Cập nhật tiến độ học tập thành công.')
  } catch (error) {
    showToast(
      handleApiError(error, 'Không thể cập nhật trạng thái.'),
      'error',
    )
  }
}

const confirmDelete = (plan) => {
  planToDelete.value = plan
}

const deletePlan = async () => {
  if (!planToDelete.value) return

  isDeleting.value = true

  try {
    await api.delete(`/study-plans/${planToDelete.value.id}`)

    plans.value = plans.value.filter(
      (plan) => plan.id !== planToDelete.value.id,
    )

    planToDelete.value = null
    showToast('Đã xóa kế hoạch học.')
  } catch (error) {
    showToast(
      handleApiError(error, 'Không thể xóa kế hoạch học.'),
      'error',
    )
  } finally {
    isDeleting.value = false
  }
}

function toInputDate(date) {
  const offset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - offset).toISOString().slice(0, 10)
}

const getPlanTimestamp = (plan) => {
  return new Date(`${plan.studyDate}T${plan.startTime || '00:00'}`).getTime()
}

const isToday = (dateValue) => {
  return dateValue === toInputDate(new Date())
}

const formatDate = (dateValue) => {
  if (!dateValue) return '---'

  return new Date(`${dateValue}T00:00:00`).toLocaleDateString('vi-VN', {
    weekday: 'long',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

const formatTime = (timeValue) => {
  return timeValue ? String(timeValue).slice(0, 5) : '--:--'
}

const getDay = (dateValue) => {
  return new Date(`${dateValue}T00:00:00`).toLocaleDateString('vi-VN', {
    day: '2-digit',
  })
}

const getMonth = (dateValue) => {
  const month = new Date(`${dateValue}T00:00:00`).getMonth() + 1
  return `TH${month}`
}

const getDurationText = (minutes) => {
  const value = Number(minutes)

  if (value < 60) {
    return `${value} phút`
  }

  const hours = Math.floor(value / 60)
  const remainMinutes = value % 60

  if (remainMinutes === 0) {
    return `${hours} giờ`
  }

  return `${hours} giờ ${remainMinutes} phút`
}


onMounted(() => {
  loadInitialData()

})
</script>
<style scoped>
.study-plan-page {
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
  align-items: center;
  justify-content: center;
}

.summary-icon.total {
  color: var(--sm-primary);
  background: var(--sm-primary-soft);
}

.summary-icon.today {
  color: var(--sm-primary-dark);
  background: var(--sm-accent-soft);
}

.summary-icon.pending {
  color: var(--sm-warning);
  background: var(--sm-warning-bg);
}

.summary-icon.done {
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

.content-card,
.side-card {
  padding: 24px;
  border: 1px solid var(--sm-border);
  border-radius: 19px;
  background: var(--sm-card);
  box-shadow: var(--sm-shadow-sm);
}

.toolbar {
  margin-bottom: 19px;
  display: flex;
  justify-content: space-between;
  gap: 18px;
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
  gap: 9px;
}

.search-box {
  width: 215px;
  height: 43px;
  padding: 0 13px;
  border: 1px solid var(--sm-border);
  border-radius: 11px;
  color: var(--sm-text-soft);
  background: #fffdfa;
  display: flex;
  align-items: center;
  gap: 8px;
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
  height: 43px;
  min-width: 133px;
  padding: 0 11px;
  border: 1px solid var(--sm-border);
  border-radius: 11px;
  outline: none;
  color: var(--sm-text);
  background: #fffdfa;
}

.date-filter-row {
  margin-bottom: 22px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f2e8dd;
  display: flex;
  gap: 9px;
}

.date-filter-btn {
  padding: 8px 16px;
  border: 1px solid var(--sm-border);
  border-radius: 22px;
  color: var(--sm-text-soft);
  background: #fffdfa;
  font-size: 14px;
  font-weight: 500;
}

.date-filter-btn.active {
  color: white;
  border-color: var(--sm-primary);
  background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
  box-shadow: 0 8px 18px rgba(185, 130, 76, 0.18);
}

.loading-state,
.api-error-state,
.empty-state {
  padding: 56px 20px;
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

.empty-state h5,
.api-error-state h5 {
  color: var(--sm-text);
  font-weight: 700;
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

.plan-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.plan-card {
  padding: 18px;
  border: 1px solid var(--sm-border);
  border-left: 5px solid var(--sm-primary);
  border-radius: 16px;
  background: #fffdfa;
  display: flex;
  gap: 17px;
  transition: 0.2s;
}

.plan-card:hover {
  border-color: var(--sm-border-strong);
  box-shadow: var(--sm-shadow-sm);
}

.plan-card.today {
  background: #fff9f1;
  border-left-color: var(--sm-accent);
}

.plan-card.completed {
  opacity: 0.76;
  border-left-color: var(--sm-success);
}

.plan-time {
  width: 78px;
  min-height: 79px;
  padding: 12px 8px;
  flex-shrink: 0;
  border-radius: 13px;
  color: var(--sm-primary-dark);
  background: var(--sm-primary-soft);
  text-align: center;
}

.plan-time strong {
  display: block;
  margin-bottom: 5px;
  font-size: 18px;
}

.plan-time span {
  color: var(--sm-primary);
  font-size: 11px;
  font-weight: 600;
}

.plan-content {
  flex: 1;
}

.plan-heading {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}

.heading-title {
  display: flex;
  align-items: center;
  gap: 9px;
  flex-wrap: wrap;
}

.heading-title h4 {
  margin: 0;
  color: var(--sm-text);
  font-size: 17px;
  font-weight: 700;
}

.today-badge {
  padding: 4px 10px;
  border-radius: 20px;
  color: var(--sm-primary-dark);
  background: var(--sm-primary-soft);
  font-size: 11px;
  font-weight: 700;
}

.plan-date {
  margin: 7px 0 0;
  color: var(--sm-text-soft);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.action-group {
  display: flex;
  gap: 7px;
}

.action-btn {
  width: 36px;
  height: 36px;
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

.plan-meta {
  margin-top: 15px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.subject-badge,
.task-badge {
  padding: 6px 11px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  display: inline-flex;
  gap: 6px;
  align-items: center;
}

.subject-badge {
  color: var(--sm-primary-dark);
  background: var(--sm-primary-soft);
}

.task-badge {
  color: var(--sm-success);
  background: var(--sm-success-bg);
}

.plan-description {
  margin: 13px 0;
  color: var(--sm-text-soft);
  font-size: 14px;
  line-height: 1.6;
}

.plan-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.status-select {
  padding: 8px 10px;
  border: none;
  border-radius: 9px;
  outline: none;
  font-size: 13px;
  font-weight: 600;
}

.status-select.chua_thuc_hien {
  color: var(--sm-danger);
  background: var(--sm-danger-bg);
}

.status-select.dang_thuc_hien {
  color: var(--sm-warning);
  background: var(--sm-warning-bg);
}

.status-select.da_hoan_thanh {
  color: var(--sm-success);
  background: var(--sm-success-bg);
}

.duration-note {
  color: var(--sm-text-soft);
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.side-header {
  margin-bottom: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.side-header h5 {
  margin: 0;
  color: var(--sm-text);
  font-weight: 700;
}

.side-header span {
  padding: 5px 10px;
  border-radius: 20px;
  color: var(--sm-primary-dark);
  background: var(--sm-primary-soft);
  font-size: 12px;
  font-weight: 600;
}

.upcoming-item {
  padding: 13px 0;
  border-bottom: 1px solid #f2e8dd;
  display: flex;
  align-items: center;
  gap: 13px;
}

.upcoming-item:last-child {
  border-bottom: none;
}

.upcoming-date {
  width: 53px;
  height: 55px;
  flex-shrink: 0;
  border-radius: 13px;
  color: var(--sm-primary-dark);
  background: var(--sm-primary-soft);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upcoming-date strong {
  font-size: 19px;
}

.upcoming-date small {
  color: var(--sm-primary);
  font-size: 11px;
  font-weight: 700;
}

.upcoming-content p {
  margin: 0 0 5px;
  color: var(--sm-text);
  font-size: 14px;
  font-weight: 600;
}

.upcoming-content small {
  color: var(--sm-text-soft);
}

.small-empty {
  padding: 22px 0;
  color: var(--sm-text-soft);
  font-size: 14px;
}

.progress-card {
  padding: 24px;
  border-radius: 19px;
  color: #fffaf4;
  background:
    radial-gradient(circle at 90% 12%, rgba(241, 221, 196, 0.25), transparent 26%),
    linear-gradient(145deg, #3b2f2a, #765139, #b9824c);
  box-shadow: 0 24px 55px rgba(90, 58, 33, 0.18);
}

.progress-icon {
  width: 49px;
  height: 49px;
  border-radius: 14px;
  background: rgba(255, 250, 244, 0.16);
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.progress-card h5 {
  margin: 16px 0;
  font-weight: 700;
}

.progress-value {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.progress-value strong {
  font-size: 38px;
}

.progress-value span {
  color: #f1ddc4;
}

.custom-progress {
  height: 9px;
  margin: 16px 0;
  border-radius: 20px;
  background: rgba(255, 250, 244, 0.22);
  overflow: hidden;
}

.custom-progress-bar {
  height: 100%;
  border-radius: 20px;
  background: #fffaf4;
  transition: width 0.3s;
}

.progress-card p {
  margin: 0;
  color: #f1ddc4;
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
  width: 690px;
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

.close-btn:hover {
  color: var(--sm-primary-dark);
  background: var(--sm-primary-soft);
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

.plan-preview {
  margin-bottom: 24px;
  padding: 15px;
  border: 1px solid var(--sm-border-strong);
  border-radius: 13px;
  background: var(--sm-accent-soft);
  display: flex;
  align-items: center;
  gap: 13px;
}

.preview-icon {
  width: 45px;
  height: 45px;
  border-radius: 12px;
  color: var(--sm-primary);
  background: var(--sm-primary-soft);
  font-size: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plan-preview p {
  margin: 0 0 4px;
  color: var(--sm-text-soft);
  font-size: 13px;
}

.plan-preview strong {
  color: var(--sm-text);
  font-size: 14px;
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

.cancel-btn:hover {
  background: var(--sm-accent-soft);
}

.save-btn {
  border: none;
  color: white;
  background: linear-gradient(135deg, var(--sm-primary), var(--sm-accent));
  display: flex;
  align-items: center;
  gap: 7px;
}

.save-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--sm-primary-dark), var(--sm-primary));
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
  align-items: center;
  justify-content: center;
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

  .filters {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {

  .page-header,
  .filters,
  .plan-heading,
  .plan-footer {
    flex-direction: column;
    align-items: flex-start;
  }

  .filters,
  .search-box,
  .filters select {
    width: 100%;
  }

  .plan-card {
    flex-direction: column;
  }

  .date-filter-row {
    overflow-x: auto;
    padding-bottom: 15px;
  }

  .date-filter-btn {
    flex-shrink: 0;
  }
}
</style>