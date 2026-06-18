<template>
  <div class="exams-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h2>Lịch thi</h2>
        <p>Theo dõi thời gian thi và thiết lập nhắc nhở qua email.</p>
      </div>

      <button class="primary-btn" @click="openAddModal">
        <i class="bi bi-plus-lg"></i>
        Thêm lịch thi
      </button>
    </div>

    <!-- Summary -->
    <div class="row g-4 mb-4">
      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon purple">
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
          <div class="summary-icon blue">
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
          <div class="summary-icon orange">
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
          <div class="summary-icon green">
            <i class="bi bi-envelope-check-fill"></i>
          </div>
          <div>
            <p>Đã bật nhắc email</p>
            <h3>{{ activeReminders }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="content-card">
      <div class="toolbar">
        <div>
          <h5>Danh sách kỳ thi</h5>
          <p>Kiểm tra lịch thi và thời điểm nhận email nhắc nhở.</p>
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

      <!-- Empty -->
      <div v-if="filteredExams.length === 0" class="empty-state">
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

      <!-- List -->
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
                  <span class="type-badge">{{ exam.examType }}</span>
                  <span
                    class="time-status"
                    :class="isPastExam(exam) ? 'past' : 'upcoming'"
                  >
                    {{ isPastExam(exam) ? 'Đã qua' : remainingText(exam) }}
                  </span>
                </div>

                <p class="subject-name">
                  <i class="bi bi-book"></i>
                  {{ getSubjectName(exam.subjectId) }}
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

              <div class="detail-item reminder-detail">
                <i class="bi bi-envelope-bell"></i>
                <div>
                  <small>Nhắc nhở email</small>

                  <p v-if="getReminder(exam.id)" class="enabled-text">
                    {{ formatDateTime(getReminder(exam.id).remindAt) }}
                  </p>

                  <p v-else class="disabled-text">Chưa bật</p>
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

    <!-- Reminder Information -->
    <div class="reminder-banner">
      <div class="reminder-banner-icon">
        <i class="bi bi-envelope-paper-heart-fill"></i>
      </div>

      <div>
        <h5>Nhắc nhở lịch thi qua email</h5>
        <p>
          Khi đến thời gian đã thiết lập, hệ thống sẽ gửi email nhắc bạn ôn tập
          và chuẩn bị cho kỳ thi sắp diễn ra.
        </p>
      </div>
    </div>

    <!-- Modal Add/Edit -->
    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-header-custom">
          <div>
            <h4>{{ isEditing ? 'Cập nhật lịch thi' : 'Thêm lịch thi mới' }}</h4>
            <p>Nhập thông tin kỳ thi và cài đặt email nhắc nhở.</p>
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
              placeholder="Ví dụ: Ôn vòng lặp, FastAPI và xử lý file..."
            ></textarea>
          </div>

          <!-- Email reminder -->
          <div class="email-setting">
            <div class="setting-header">
              <div>
                <h5>Nhắc nhở qua email</h5>
                <p>Gửi email trước khi kỳ thi diễn ra.</p>
              </div>

              <label class="switch">
                <input v-model="form.enableReminder" type="checkbox" />
                <span class="slider"></span>
              </label>
            </div>

            <div v-if="form.enableReminder" class="email-fields">
              <div class="form-group">
                <label>Email nhận thông báo <span>*</span></label>
                <input
                  v-model.trim="form.emailTo"
                  type="email"
                  placeholder="vothithaingoc072005@gmail.com"
                  :class="{ invalid: errors.emailTo }"
                />
                <small v-if="errors.emailTo" class="error-text">
                  {{ errors.emailTo }}
                </small>
              </div>

              <div class="form-group mb-0">
                <label>Thời gian gửi email <span>*</span></label>
                <input
                  v-model="form.remindAt"
                  type="datetime-local"
                  :class="{ invalid: errors.remindAt }"
                />
                <small v-if="errors.remindAt" class="error-text">
                  {{ errors.remindAt }}
                </small>
              </div>
            </div>
          </div>

          <div class="modal-footer-custom">
            <button type="button" class="cancel-btn" @click="closeModal">
              Hủy
            </button>

            <button type="submit" class="save-btn">
              <i class="bi bi-check-lg"></i>
              {{ isEditing ? 'Lưu thay đổi' : 'Thêm lịch thi' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation -->
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

          <button class="confirm-delete-btn" @click="deleteExam">
            Xóa lịch thi
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

const examStorageKey = 'studymate_exams'
const reminderStorageKey = 'studymate_reminders'
const subjectStorageKey = 'studymate_subjects'

const createFutureDatetime = (days, hour = 7, minute = 0) => {
  const date = new Date()
  date.setDate(date.getDate() + days)
  date.setHours(hour, minute, 0, 0)

  const offset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - offset).toISOString().slice(0, 16)
}

const createReminderDatetime = (examDatetime, daysBefore = 3) => {
  const date = new Date(examDatetime)
  date.setDate(date.getDate() - daysBefore)
  date.setHours(8, 0, 0, 0)

  const offset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - offset).toISOString().slice(0, 16)
}

const defaultSubjects = [
  { id: 1, name: 'Perl & Python' },
  { id: 2, name: 'System Integration' },
  { id: 3, name: 'Cơ sở dữ liệu' },
]

const loadSubjects = () => {
  const data = localStorage.getItem(subjectStorageKey)
  return data ? JSON.parse(data) : defaultSubjects
}

const subjects = ref(loadSubjects())

const exam1Datetime = createFutureDatetime(10)
const exam2Datetime = createFutureDatetime(15, 9, 0)
const exam3Datetime = createFutureDatetime(6, 13, 30)

const defaultExams = [
  {
    id: 1,
    subjectId: '1',
    title: 'Thi kết thúc môn Perl & Python',
    examType: 'Cuối kỳ',
    examDatetime: exam1Datetime,
    location: 'P.301',
    note: 'Ôn Python, Perl, FastAPI và xử lý file.',
  },
  {
    id: 2,
    subjectId: '2',
    title: 'Thi System Integration',
    examType: 'Cuối kỳ',
    examDatetime: exam2Datetime,
    location: 'P.405',
    note: 'Ôn Integration Models, Messaging và API Gateway.',
  },
  {
    id: 3,
    subjectId: '3',
    title: 'Kiểm tra SQL',
    examType: 'Giữa kỳ',
    examDatetime: exam3Datetime,
    location: 'Phòng Lab 2',
    note: 'Ôn JOIN, VIEW và khóa ngoại.',
  },
]

const defaultReminders = [
  {
    id: 1,
    targetType: 'EXAM',
    examId: 1,
    remindAt: createReminderDatetime(exam1Datetime, 3),
    emailTo: 'vothithaingoc072005@gmail.com',
    status: 'PENDING',
  },
  {
    id: 2,
    targetType: 'EXAM',
    examId: 3,
    remindAt: createReminderDatetime(exam3Datetime, 2),
    emailTo: 'vothithaingoc072005@gmail.com',
    status: 'PENDING',
  },
]

const loadData = (key, defaultData) => {
  const data = localStorage.getItem(key)

  if (data) {
    return JSON.parse(data)
  }

  localStorage.setItem(key, JSON.stringify(defaultData))
  return defaultData
}

const exams = ref(loadData(examStorageKey, defaultExams))
const reminders = ref(loadData(reminderStorageKey, defaultReminders))

const searchKeyword = ref('')
const selectedSubject = ref('')
const selectedTimeFilter = ref('')

const isModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const examToDelete = ref(null)
const toastMessage = ref('')

const emptyForm = () => {
  const examDatetime = createFutureDatetime(7)

  return {
    title: '',
    subjectId: '',
    examType: 'Cuối kỳ',
    examDatetime,
    location: '',
    note: '',
    enableReminder: true,
    emailTo: 'vothithaingoc072005@gmail.com',
    remindAt: createReminderDatetime(examDatetime, 3),
  }
}

const form = ref(emptyForm())

const errors = ref({
  title: '',
  subjectId: '',
  examDatetime: '',
  emailTo: '',
  remindAt: '',
})

const upcomingExams = computed(() => {
  return exams.value.filter((exam) => !isPastExam(exam)).length
})

const examsInSevenDays = computed(() => {
  return exams.value.filter((exam) => {
    const days = getDaysRemaining(exam)
    return days >= 0 && days <= 7
  }).length
})

const activeReminders = computed(() => {
  return reminders.value.filter(
    (reminder) =>
      reminder.targetType === 'EXAM' && reminder.status === 'PENDING',
  ).length
})

const filteredExams = computed(() => {
  const keyword = searchKeyword.value.toLowerCase()

  return [...exams.value]
    .filter((exam) => {
      const matchesKeyword =
        exam.title.toLowerCase().includes(keyword) ||
        getSubjectName(exam.subjectId).toLowerCase().includes(keyword) ||
        exam.location.toLowerCase().includes(keyword)

      const matchesSubject =
        !selectedSubject.value || String(exam.subjectId) === selectedSubject.value

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

const persistData = () => {
  localStorage.setItem(examStorageKey, JSON.stringify(exams.value))
  localStorage.setItem(reminderStorageKey, JSON.stringify(reminders.value))
}

const getSubjectName = (subjectId) => {
  const subject = subjects.value.find(
    (item) => String(item.id) === String(subjectId),
  )

  return subject ? subject.name : 'Không xác định'
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

const getDaysRemaining = (exam) => {
  const milliseconds =
    new Date(exam.examDatetime).getTime() - new Date().getTime()

  return Math.ceil(milliseconds / (1000 * 60 * 60 * 24))
}

const isPastExam = (exam) => {
  return new Date(exam.examDatetime).getTime() < new Date().getTime()
}

const remainingText = (exam) => {
  const days = getDaysRemaining(exam)

  if (days === 0) {
    return 'Thi hôm nay'
  }

  if (days === 1) {
    return 'Còn 1 ngày'
  }

  return `Còn ${days} ngày`
}

const getReminder = (examId) => {
  return reminders.value.find(
    (reminder) =>
      Number(reminder.examId) === Number(examId) &&
      reminder.targetType === 'EXAM' &&
      reminder.status !== 'CANCELLED',
  )
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
    examDatetime: '',
    emailTo: '',
    remindAt: '',
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
  const reminder = getReminder(exam.id)

  isEditing.value = true
  editingId.value = exam.id
  form.value = {
    ...exam,
    enableReminder: Boolean(reminder),
    emailTo: reminder?.emailTo || 'vothithaingoc072005@gmail.com',
    remindAt:
      reminder?.remindAt || createReminderDatetime(exam.examDatetime, 3),
  }

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

  if (form.value.enableReminder) {
    if (!form.value.emailTo) {
      errors.value.emailTo = 'Vui lòng nhập email nhận thông báo.'
      valid = false
    }

    if (!form.value.remindAt) {
      errors.value.remindAt = 'Vui lòng chọn thời gian gửi email.'
      valid = false
    } else if (
      new Date(form.value.remindAt).getTime() >=
      new Date(form.value.examDatetime).getTime()
    ) {
      errors.value.remindAt = 'Thời gian nhắc phải trước thời gian thi.'
      valid = false
    }
  }

  return valid
}

const saveReminderForExam = (examId) => {
  const reminderIndex = reminders.value.findIndex(
    (reminder) =>
      Number(reminder.examId) === Number(examId) &&
      reminder.targetType === 'EXAM',
  )

  if (!form.value.enableReminder) {
    if (reminderIndex !== -1) {
      reminders.value.splice(reminderIndex, 1)
    }

    return
  }

  const reminderData = {
    id: reminderIndex !== -1 ? reminders.value[reminderIndex].id : Date.now(),
    targetType: 'EXAM',
    examId,
    remindAt: form.value.remindAt,
    emailTo: form.value.emailTo,
    status: 'PENDING',
  }

  if (reminderIndex !== -1) {
    reminders.value[reminderIndex] = reminderData
  } else {
    reminders.value.push(reminderData)
  }
}

const saveExam = () => {
  if (!validateForm()) {
    return
  }

  const examData = {
    subjectId: form.value.subjectId,
    title: form.value.title,
    examType: form.value.examType,
    examDatetime: form.value.examDatetime,
    location: form.value.location,
    note: form.value.note,
  }

  let examId

  if (isEditing.value) {
    const index = exams.value.findIndex((exam) => exam.id === editingId.value)

    exams.value[index] = {
      ...exams.value[index],
      ...examData,
    }

    examId = editingId.value
    showToast('Cập nhật lịch thi thành công.')
  } else {
    examId = Date.now()

    exams.value.unshift({
      id: examId,
      ...examData,
    })

    showToast('Thêm lịch thi thành công.')
  }

  saveReminderForExam(examId)
  persistData()
  closeModal()
}

const confirmDelete = (exam) => {
  examToDelete.value = exam
}

const deleteExam = () => {
  const deletedId = examToDelete.value.id

  exams.value = exams.value.filter((exam) => exam.id !== deletedId)

  reminders.value = reminders.value.filter(
    (reminder) => Number(reminder.examId) !== Number(deletedId),
  )

  persistData()
  examToDelete.value = null
  showToast('Đã xóa lịch thi thành công.')
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
  font-size: 28px;
  font-weight: 700;
}

.content-card {
  padding: 24px;
  border-radius: 19px;
  border: 1px solid #edf0f5;
  background: white;
}

.toolbar {
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  gap: 20px;
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
  gap: 10px;
}

.search-box {
  width: 245px;
  height: 44px;
  padding: 0 14px;
  border: 1px solid #e5e7eb;
  border-radius: 11px;
  display: flex;
  align-items: center;
  gap: 9px;
  color: #6b7280;
}

.search-box input {
  width: 100%;
  border: none;
  outline: none;
}

.filters select {
  height: 44px;
  min-width: 145px;
  padding: 0 12px;
  border: 1px solid #e5e7eb;
  border-radius: 11px;
  color: #374151;
  background: white;
}

.exam-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.exam-card {
  padding: 20px;
  border: 1px solid #edf0f5;
  border-radius: 17px;
  display: flex;
  gap: 18px;
  transition: 0.2s;
}

.exam-card:hover {
  border-color: #c7d2fe;
  box-shadow: 0 5px 18px rgba(15, 23, 42, 0.05);
}

.exam-card.passed {
  opacity: 0.72;
}

.date-box {
  width: 67px;
  height: 72px;
  flex-shrink: 0;
  border-radius: 16px;
  background: #eef2ff;
  color: #4338ca;
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
  color: #6366f1;
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
  color: #111827;
  font-size: 18px;
  font-weight: 700;
}

.type-badge {
  padding: 5px 10px;
  border-radius: 20px;
  color: #4338ca;
  background: #eef2ff;
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
  color: #ea580c;
  background: #fff7ed;
}

.time-status.past {
  color: #6b7280;
  background: #f3f4f6;
}

.subject-name {
  margin: 8px 0 0;
  color: #6b7280;
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
  color: #ea580c;
  background: #fff7ed;
}

.action-btn.delete {
  color: #dc2626;
  background: #fef2f2;
}

.exam-details {
  margin-top: 19px;
  display: flex;
  flex-wrap: wrap;
  gap: 35px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 185px;
}

.detail-item > i {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  color: #6366f1;
  background: #eef2ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-item small {
  display: block;
  color: #6b7280;
  margin-bottom: 3px;
}

.detail-item p {
  margin: 0;
  color: #111827;
  font-size: 14px;
  font-weight: 500;
}

.detail-item .enabled-text {
  color: #15803d;
}

.detail-item .disabled-text {
  color: #9ca3af;
}

.exam-note {
  margin-top: 18px;
  padding: 11px 14px;
  border-radius: 10px;
  color: #4b5563;
  background: #f8fafc;
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 14px;
}

.reminder-banner {
  margin-top: 22px;
  padding: 21px 24px;
  border-radius: 17px;
  border: 1px solid #bfdbfe;
  background: #eff6ff;
  display: flex;
  align-items: center;
  gap: 18px;
}

.reminder-banner-icon {
  width: 55px;
  height: 55px;
  border-radius: 15px;
  color: #2563eb;
  background: #dbeafe;
  font-size: 25px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.reminder-banner h5 {
  margin: 0 0 6px;
  color: #1e3a8a;
  font-weight: 700;
}

.reminder-banner p {
  margin: 0;
  color: #2563eb;
  font-size: 14px;
}

.empty-state {
  padding: 55px 20px;
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
  width: 680px;
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

.email-setting {
  margin: 4px 0 24px;
  padding: 17px;
  border-radius: 14px;
  border: 1px solid #e0e7ff;
  background: #f8faff;
}

.setting-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.setting-header h5 {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 700;
}

.setting-header p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

.email-fields {
  margin-top: 19px;
  padding-top: 18px;
  border-top: 1px solid #e0e7ff;
}

.switch {
  position: relative;
  width: 48px;
  height: 27px;
}

.switch input {
  display: none;
}

.slider {
  position: absolute;
  inset: 0;
  cursor: pointer;
  border-radius: 30px;
  background: #d1d5db;
}

.slider::before {
  position: absolute;
  content: '';
  left: 4px;
  top: 4px;
  width: 19px;
  height: 19px;
  border-radius: 50%;
  background: white;
  transition: 0.2s;
}

.switch input:checked + .slider {
  background: #6366f1;
}

.switch input:checked + .slider::before {
  transform: translateX(21px);
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
  justify-content: center;
  align-items: center;
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
  .exam-heading,
  .setting-header {
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
}
</style>