<template>
  <div class="study-plan-page">
    <!-- Header -->
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

    <!-- Summary -->
    <div class="row g-4 mb-4">
      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon purple">
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
          <div class="summary-icon blue">
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
          <div class="summary-icon orange">
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
          <div class="summary-icon green">
            <i class="bi bi-stopwatch-fill"></i>
          </div>

          <div>
            <p>Tổng thời gian học</p>
            <h3>{{ totalStudyHours }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="row g-4">
      <!-- Danh sách kế hoạch -->
      <div class="col-xl-8">
        <div class="content-card">
          <div class="toolbar">
            <div>
              <h5>Lịch ôn tập của bạn</h5>
              <p>Theo dõi các buổi học và nội dung cần hoàn thành.</p>
            </div>

            <div class="filters">
              <div class="search-box">
                <i class="bi bi-search"></i>
                <input
                  v-model="searchKeyword"
                  type="text"
                  placeholder="Tìm kế hoạch..."
                />
              </div>

              <select v-model="selectedSubject">
                <option value="">Tất cả môn</option>
                <option
                  v-for="subject in subjects"
                  :key="subject.id"
                  :value="String(subject.id)"
                >
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

          <!-- Date Filters -->
          <div class="date-filter-row">
            <button
              v-for="filter in dateFilters"
              :key="filter.value"
              class="date-filter-btn"
              :class="{ active: selectedDateFilter === filter.value }"
              @click="selectedDateFilter = filter.value"
            >
              {{ filter.label }}
            </button>
          </div>

          <!-- Empty -->
          <div v-if="filteredPlans.length === 0" class="empty-state">
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

          <!-- Plan List -->
          <div v-else class="plan-list">
            <div
              v-for="plan in filteredPlans"
              :key="plan.id"
              class="plan-card"
              :class="{
                completed: plan.status === 'DA_HOAN_THANH',
                today: isToday(plan.studyDate),
              }"
            >
              <div class="plan-time">
                <strong>{{ formatTime(plan.startTime) }}</strong>
                <span>{{ plan.durationMinutes }} phút</span>
              </div>

              <div class="plan-content">
                <div class="plan-heading">
                  <div>
                    <div class="heading-title">
                      <h4>{{ plan.title }}</h4>

                      <span
                        v-if="isToday(plan.studyDate)"
                        class="today-badge"
                      >
                        Hôm nay
                      </span>
                    </div>

                    <p class="plan-date">
                      <i class="bi bi-calendar3"></i>
                      {{ formatDate(plan.studyDate) }}
                    </p>
                  </div>

                  <div class="action-group">
                    <button
                      class="action-btn edit"
                      title="Sửa kế hoạch"
                      @click="openEditModal(plan)"
                    >
                      <i class="bi bi-pencil-square"></i>
                    </button>

                    <button
                      class="action-btn delete"
                      title="Xóa kế hoạch"
                      @click="confirmDelete(plan)"
                    >
                      <i class="bi bi-trash3"></i>
                    </button>
                  </div>
                </div>

                <div class="plan-meta">
                  <span class="subject-badge">
                    <i class="bi bi-book"></i>
                    {{ getSubjectName(plan.subjectId) }}
                  </span>

                  <span
                    v-if="getTaskName(plan.taskId)"
                    class="task-badge"
                  >
                    <i class="bi bi-check2-square"></i>
                    {{ getTaskName(plan.taskId) }}
                  </span>
                </div>

                <p class="plan-description">
                  {{ plan.content || 'Chưa có nội dung ôn tập cụ thể.' }}
                </p>

                <div class="plan-footer">
                  <select
                    class="status-select"
                    :class="plan.status.toLowerCase()"
                    :value="plan.status"
                    @change="changeStatus(plan, $event.target.value)"
                  >
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

          <div
            v-for="plan in upcomingPlans.slice(0, 4)"
            :key="plan.id"
            class="upcoming-item"
          >
            <div class="upcoming-date">
              <strong>{{ getDay(plan.studyDate) }}</strong>
              <small>{{ getMonth(plan.studyDate) }}</small>
            </div>

            <div class="upcoming-content">
              <p>{{ plan.title }}</p>
              <small>
                {{ formatTime(plan.startTime) }} ·
                {{ getSubjectName(plan.subjectId) }}
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
            <div
              class="custom-progress-bar"
              :style="{ width: `${completionPercent}%` }"
            ></div>
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
            <input
              v-model.trim="form.title"
              type="text"
              placeholder="Ví dụ: Ôn Python buổi tối"
              :class="{ invalid: errors.title }"
            />
            <small v-if="errors.title" class="error-text">
              {{ errors.title }}
            </small>
          </div>

          <div class="row g-3">
            <div class="col-md-6">
              <div class="form-group">
                <label>Môn học <span>*</span></label>
                <select
                  v-model="form.subjectId"
                  :class="{ invalid: errors.subjectId }"
                  @change="form.taskId = ''"
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

            <div class="col-md-6">
              <div class="form-group">
                <label>Bài tập liên quan</label>
                <select v-model="form.taskId">
                  <option value="">Không liên kết bài tập</option>
                  <option
                    v-for="task in availableTasks"
                    :key="task.id"
                    :value="String(task.id)"
                  >
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
                <input
                  v-model="form.studyDate"
                  type="date"
                  :class="{ invalid: errors.studyDate }"
                />
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
            <textarea
              v-model.trim="form.content"
              rows="4"
              placeholder="Ví dụ: Ôn vòng lặp for, while và làm bài tập minh họa..."
            ></textarea>
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

            <button type="submit" class="save-btn">
              <i class="bi bi-check-lg"></i>
              {{ isEditing ? 'Lưu thay đổi' : 'Tạo kế hoạch' }}
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

          <button class="confirm-delete-btn" @click="deletePlan">
            Xóa kế hoạch
          </button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toastMessage" class="toast-message">
      <i class="bi bi-check-circle-fill"></i>
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const studyPlanStorageKey = 'studymate_study_plans'
const subjectStorageKey = 'studymate_subjects'
const taskStorageKey = 'studymate_tasks'

const toInputDate = (date) => {
  const offset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - offset).toISOString().slice(0, 10)
}

const createDateFromToday = (days) => {
  const date = new Date()
  date.setDate(date.getDate() + days)
  return toInputDate(date)
}

const defaultSubjects = [
  { id: 1, name: 'Perl & Python' },
  { id: 2, name: 'System Integration' },
  { id: 3, name: 'Cơ sở dữ liệu' },
  { id: 4, name: 'Lập trình Web' },
]

const defaultTasks = [
  {
    id: 1,
    subjectId: '1',
    title: 'Ôn vòng lặp và hàm trong Python',
  },
  {
    id: 2,
    subjectId: '1',
    title: 'Xây dựng API FastAPI cho chatbot',
  },
  {
    id: 3,
    subjectId: '2',
    title: 'Ôn mô hình tích hợp dữ liệu',
  },
]

const loadData = (key, defaultData) => {
  const data = localStorage.getItem(key)
  return data ? JSON.parse(data) : defaultData
}

const subjects = ref(loadData(subjectStorageKey, defaultSubjects))
const tasks = ref(loadData(taskStorageKey, defaultTasks))

const defaultPlans = [
  {
    id: 1,
    subjectId: '1',
    taskId: '1',
    title: 'Ôn Python buổi tối',
    content: 'Ôn vòng lặp for, while và viết 5 ví dụ minh họa.',
    studyDate: createDateFromToday(0),
    startTime: '19:00',
    durationMinutes: 120,
    status: 'DANG_THUC_HIEN',
  },
  {
    id: 2,
    subjectId: '1',
    taskId: '2',
    title: 'Thực hành FastAPI',
    content: 'Tạo route /chat và kiểm tra request, response.',
    studyDate: createDateFromToday(1),
    startTime: '20:00',
    durationMinutes: 90,
    status: 'CHUA_THUC_HIEN',
  },
  {
    id: 3,
    subjectId: '2',
    taskId: '3',
    title: 'Ôn System Integration',
    content: 'Ôn Data Integration, Functional Integration và Messaging.',
    studyDate: createDateFromToday(2),
    startTime: '18:30',
    durationMinutes: 90,
    status: 'CHUA_THUC_HIEN',
  },
  {
    id: 4,
    subjectId: '3',
    taskId: '',
    title: 'Ôn SQL và ERD',
    content: 'Xem lại quan hệ bảng, khóa ngoại và view.',
    studyDate: createDateFromToday(-1),
    startTime: '19:30',
    durationMinutes: 60,
    status: 'DA_HOAN_THANH',
  },
]

const loadPlans = () => {
  const data = localStorage.getItem(studyPlanStorageKey)

  if (data) {
    return JSON.parse(data)
  }

  localStorage.setItem(studyPlanStorageKey, JSON.stringify(defaultPlans))
  return defaultPlans
}

const plans = ref(loadPlans())

const searchKeyword = ref('')
const selectedSubject = ref('')
const selectedStatus = ref('')
const selectedDateFilter = ref('ALL')

const isModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const planToDelete = ref(null)
const toastMessage = ref('')

const dateFilters = [
  { label: 'Tất cả', value: 'ALL' },
  { label: 'Hôm nay', value: 'TODAY' },
  { label: 'Sắp tới', value: 'UPCOMING' },
  { label: 'Đã qua', value: 'PAST' },
]

const emptyForm = () => ({
  subjectId: '',
  taskId: '',
  title: '',
  content: '',
  studyDate: createDateFromToday(0),
  startTime: '19:00',
  durationMinutes: 60,
  status: 'CHUA_THUC_HIEN',
})

const form = ref(emptyForm())

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
    .sort((first, second) => {
      return getPlanTimestamp(first) - getPlanTimestamp(second)
    })
})

const availableTasks = computed(() => {
  if (!form.value.subjectId) return []

  return tasks.value.filter(
    (task) => String(task.subjectId) === String(form.value.subjectId),
  )
})

const filteredPlans = computed(() => {
  const keyword = searchKeyword.value.toLowerCase()

  return [...plans.value]
    .filter((plan) => {
      const matchesKeyword =
        plan.title.toLowerCase().includes(keyword) ||
        plan.content.toLowerCase().includes(keyword) ||
        getSubjectName(plan.subjectId).toLowerCase().includes(keyword)

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

const persistPlans = () => {
  localStorage.setItem(studyPlanStorageKey, JSON.stringify(plans.value))
}

const getPlanTimestamp = (plan) => {
  return new Date(`${plan.studyDate}T${plan.startTime || '00:00'}`).getTime()
}

const getSubjectName = (subjectId) => {
  const subject = subjects.value.find(
    (item) => String(item.id) === String(subjectId),
  )

  return subject ? subject.name : 'Không xác định'
}

const getTaskName = (taskId) => {
  if (!taskId) return ''

  const task = tasks.value.find((item) => String(item.id) === String(taskId))

  return task ? task.title : ''
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
  return timeValue || '--:--'
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

const showToast = (message) => {
  toastMessage.value = message

  setTimeout(() => {
    toastMessage.value = ''
  }, 2600)
}

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
  form.value = { ...plan }
  resetErrors()
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  resetErrors()
}

const validateForm = () => {
  resetErrors()
  let valid = true

  if (!form.value.title) {
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

const savePlan = () => {
  if (!validateForm()) return

  const planData = {
    subjectId: form.value.subjectId,
    taskId: form.value.taskId,
    title: form.value.title,
    content: form.value.content,
    studyDate: form.value.studyDate,
    startTime: form.value.startTime,
    durationMinutes: form.value.durationMinutes,
    status: form.value.status,
  }

  if (isEditing.value) {
    const index = plans.value.findIndex((plan) => plan.id === editingId.value)

    plans.value[index] = {
      ...plans.value[index],
      ...planData,
    }

    showToast('Cập nhật kế hoạch thành công.')
  } else {
    plans.value.unshift({
      id: Date.now(),
      ...planData,
    })

    showToast('Tạo kế hoạch học thành công.')
  }

  persistPlans()
  closeModal()
}

const changeStatus = (plan, status) => {
  plan.status = status
  persistPlans()
  showToast('Cập nhật tiến độ học tập thành công.')
}

const confirmDelete = (plan) => {
  planToDelete.value = plan
}

const deletePlan = () => {
  plans.value = plans.value.filter((plan) => plan.id !== planToDelete.value.id)

  persistPlans()
  planToDelete.value = null
  showToast('Đã xóa kế hoạch học.')
}
</script>

<style scoped>
.page-header {
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-header h2 {
  margin: 0 0 7px;
  color: #111827;
  font-size: 27px;
  font-weight: 700;
}

.page-header p {
  margin: 0;
  color: #6b7280;
}

.primary-btn {
  height: 47px;
  padding: 0 20px;
  border: none;
  border-radius: 12px;
  color: white;
  background: #6366f1;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  transition: 0.2s;
}

.primary-btn:hover {
  background: #4f46e5;
}

.summary-card {
  height: 110px;
  padding: 22px;
  border-radius: 18px;
  border: 1px solid #edf0f5;
  background: white;
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

.summary-icon.purple {
  color: #6366f1;
  background: #eef2ff;
}

.summary-icon.blue {
  color: #2563eb;
  background: #eff6ff;
}

.summary-icon.orange {
  color: #f97316;
  background: #fff7ed;
}

.summary-icon.green {
  color: #16a34a;
  background: #f0fdf4;
}

.summary-card p {
  margin: 0 0 6px;
  color: #6b7280;
  font-size: 14px;
}

.summary-card h3 {
  margin: 0;
  color: #111827;
  font-size: 28px;
  font-weight: 700;
}

.content-card,
.side-card {
  padding: 24px;
  border-radius: 19px;
  border: 1px solid #edf0f5;
  background: white;
}

.toolbar {
  margin-bottom: 19px;
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.toolbar h5 {
  margin: 0 0 5px;
  font-weight: 700;
}

.toolbar p {
  margin: 0;
  color: #6b7280;
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
  border: 1px solid #e5e7eb;
  border-radius: 11px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6b7280;
}

.search-box input {
  width: 100%;
  border: none;
  outline: none;
}

.filters select {
  height: 43px;
  min-width: 133px;
  padding: 0 11px;
  border: 1px solid #e5e7eb;
  border-radius: 11px;
  color: #374151;
  background: white;
}

.date-filter-row {
  margin-bottom: 22px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  gap: 9px;
}

.date-filter-btn {
  padding: 8px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 22px;
  color: #6b7280;
  background: white;
  font-size: 14px;
  font-weight: 500;
}

.date-filter-btn.active {
  color: white;
  border-color: #6366f1;
  background: #6366f1;
}

.plan-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.plan-card {
  padding: 18px;
  border: 1px solid #edf0f5;
  border-radius: 16px;
  display: flex;
  gap: 17px;
  transition: 0.2s;
}

.plan-card:hover {
  border-color: #c7d2fe;
  box-shadow: 0 5px 17px rgba(15, 23, 42, 0.05);
}

.plan-card.today {
  border-color: #c7d2fe;
  background: #fafaff;
}

.plan-card.completed {
  opacity: 0.75;
}

.plan-time {
  width: 78px;
  min-height: 79px;
  padding: 12px 8px;
  flex-shrink: 0;
  border-radius: 13px;
  color: #4338ca;
  background: #eef2ff;
  text-align: center;
}

.plan-time strong {
  display: block;
  margin-bottom: 5px;
  font-size: 18px;
}

.plan-time span {
  color: #6366f1;
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
}

.heading-title h4 {
  margin: 0;
  color: #111827;
  font-size: 17px;
  font-weight: 700;
}

.today-badge {
  padding: 4px 10px;
  border-radius: 20px;
  color: #2563eb;
  background: #dbeafe;
  font-size: 11px;
  font-weight: 700;
}

.plan-date {
  margin: 7px 0 0;
  color: #6b7280;
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
  color: #ea580c;
  background: #fff7ed;
}

.action-btn.delete {
  color: #dc2626;
  background: #fef2f2;
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
  color: #4338ca;
  background: #eef2ff;
}

.task-badge {
  color: #0369a1;
  background: #f0f9ff;
}

.plan-description {
  margin: 13px 0;
  color: #4b5563;
  font-size: 14px;
}

.plan-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  color: #dc2626;
  background: #fef2f2;
}

.status-select.dang_thuc_hien {
  color: #ea580c;
  background: #fff7ed;
}

.status-select.da_hoan_thanh {
  color: #15803d;
  background: #f0fdf4;
}

.duration-note {
  color: #6b7280;
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
  font-weight: 700;
}

.side-header span {
  padding: 5px 10px;
  border-radius: 20px;
  color: #4338ca;
  background: #eef2ff;
  font-size: 12px;
  font-weight: 600;
}

.upcoming-item {
  padding: 13px 0;
  border-bottom: 1px solid #f1f5f9;
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
  border-radius: 13px;
  color: #4338ca;
  background: #eef2ff;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.upcoming-date strong {
  font-size: 19px;
}

.upcoming-date small {
  color: #6366f1;
  font-size: 11px;
  font-weight: 700;
}

.upcoming-content p {
  margin: 0 0 5px;
  color: #111827;
  font-size: 14px;
  font-weight: 600;
}

.upcoming-content small {
  color: #6b7280;
}

.small-empty {
  padding: 22px 0;
  color: #6b7280;
  font-size: 14px;
}

.progress-card {
  padding: 24px;
  border-radius: 19px;
  color: white;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
}

.progress-icon {
  width: 49px;
  height: 49px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.17);
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
  color: #e0e7ff;
}

.custom-progress {
  height: 9px;
  margin: 16px 0;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.22);
  overflow: hidden;
}

.custom-progress-bar {
  height: 100%;
  border-radius: 20px;
  background: white;
  transition: width 0.3s;
}

.progress-card p {
  margin: 0;
  color: #e0e7ff;
  font-size: 14px;
}

.empty-state {
  padding: 56px 20px;
  text-align: center;
}

.empty-icon {
  width: 68px;
  height: 68px;
  margin: 0 auto 18px;
  border-radius: 50%;
  color: #6366f1;
  background: #eef2ff;
  font-size: 31px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.empty-state h5 {
  font-weight: 700;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 22px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 300;
  padding: 22px;
  background: rgba(15, 23, 42, 0.48);
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
  border-radius: 20px;
  background: white;
}

.modal-header-custom {
  margin-bottom: 23px;
  display: flex;
  justify-content: space-between;
}

.modal-header-custom h4 {
  margin: 0 0 6px;
  font-weight: 700;
}

.modal-header-custom p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.close-btn {
  width: 38px;
  height: 38px;
  border: none;
  border-radius: 9px;
  background: #f3f4f6;
}

.form-group {
  margin-bottom: 18px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #374151;
  font-size: 14px;
  font-weight: 600;
}

.form-group label span {
  color: #dc2626;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px 13px;
  border: 1px solid #e5e7eb;
  border-radius: 11px;
  outline: none;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #6366f1;
}

.form-group .invalid {
  border-color: #dc2626;
}

.error-text {
  display: block;
  margin-top: 6px;
  color: #dc2626;
  font-size: 12px;
}

.plan-preview {
  margin-bottom: 24px;
  padding: 15px;
  border-radius: 13px;
  background: #f8faff;
  border: 1px solid #e0e7ff;
  display: flex;
  align-items: center;
  gap: 13px;
}

.preview-icon {
  width: 45px;
  height: 45px;
  border-radius: 12px;
  color: #6366f1;
  background: #eef2ff;
  font-size: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plan-preview p {
  margin: 0 0 4px;
  color: #6b7280;
  font-size: 13px;
}

.plan-preview strong {
  color: #111827;
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
  border: 1px solid #e5e7eb;
  color: #374151;
  background: white;
}

.save-btn {
  border: none;
  color: white;
  background: #6366f1;
  display: flex;
  align-items: center;
  gap: 7px;
}

.delete-modal {
  width: 420px;
  max-width: 100%;
  padding: 31px;
  border-radius: 20px;
  background: white;
  text-align: center;
}

.delete-icon {
  width: 62px;
  height: 62px;
  margin: 0 auto 18px;
  border-radius: 50%;
  color: #dc2626;
  background: #fef2f2;
  font-size: 27px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-modal h4 {
  font-weight: 700;
}

.delete-modal p {
  margin: 12px 0 25px;
  color: #6b7280;
}

.delete-actions {
  display: flex;
  justify-content: center;
  gap: 11px;
}

.confirm-delete-btn {
  border: none;
  color: white;
  background: #dc2626;
}

.toast-message {
  position: fixed;
  z-index: 500;
  top: 94px;
  right: 28px;
  padding: 14px 18px;
  border-radius: 11px;
  color: white;
  background: #16a34a;
  display: flex;
  align-items: center;
  gap: 9px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.15);
}

@media (max-width: 1200px) {
  .toolbar {
    flex-direction: column;
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
  }
}
</style>