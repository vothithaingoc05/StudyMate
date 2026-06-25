<template>
  <div class="reminders-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h2>Nhắc nhở Email</h2>
        <p>Thiết lập thông báo deadline và lịch thi để không bỏ lỡ công việc quan trọng.</p>
      </div>

      <button class="primary-btn" @click="openAddModal">
        <i class="bi bi-plus-lg"></i>
        Tạo nhắc nhở
      </button>
    </div>

    <!-- Summary -->
    <div class="row g-4 mb-4">
      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon purple">
            <i class="bi bi-bell-fill"></i>
          </div>

          <div>
            <p>Tổng nhắc nhở</p>
            <h3>{{ reminders.length }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon orange">
            <i class="bi bi-hourglass-split"></i>
          </div>

          <div>
            <p>Đang chờ gửi</p>
            <h3>{{ pendingCount }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon red">
            <i class="bi bi-exclamation-circle-fill"></i>
          </div>

          <div>
            <p>Đã đến giờ gửi</p>
            <h3>{{ dueCount }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon green">
            <i class="bi bi-envelope-check-fill"></i>
          </div>

          <div>
            <p>Đã gửi thành công</p>
            <h3>{{ sentCount }}</h3>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <!-- Settings -->
      <div class="col-xl-4">
        <div class="settings-card">
          <div class="settings-title">
            <div class="settings-icon">
              <i class="bi bi-gear-fill"></i>
            </div>

            <div>
              <h5>Cài đặt mặc định</h5>
              <p>Áp dụng khi tạo nhắc nhở mới.</p>
            </div>
          </div>

          <div class="email-toggle">
            <div>
              <strong>Nhận email nhắc nhở</strong>
              <small>Bật thông báo học tập qua email</small>
            </div>

            <label class="switch">
              <input v-model="settings.emailEnabled" type="checkbox" />
              <span class="slider"></span>
            </label>
          </div>

          <div class="setting-form">
            <div class="form-group">
              <label>Email nhận thông báo</label>
              <input
                v-model.trim="settings.email"
                type="email"
                placeholder="vothithaingoc072005@gmail.com"
              />
            </div>

            <div class="form-group">
              <label>Nhắc bài tập trước deadline</label>
              <select v-model.number="settings.defaultTaskReminderDays">
                <option :value="0">Trong ngày</option>
                <option :value="1">Trước 1 ngày</option>
                <option :value="2">Trước 2 ngày</option>
                <option :value="3">Trước 3 ngày</option>
                <option :value="7">Trước 7 ngày</option>
              </select>
            </div>

            <div class="form-group">
              <label>Nhắc lịch thi trước ngày thi</label>
              <select v-model.number="settings.defaultExamReminderDays">
                <option :value="1">Trước 1 ngày</option>
                <option :value="2">Trước 2 ngày</option>
                <option :value="3">Trước 3 ngày</option>
                <option :value="5">Trước 5 ngày</option>
                <option :value="7">Trước 7 ngày</option>
              </select>
            </div>

            <div class="form-group">
              <label>Giờ gửi mặc định</label>
              <input v-model="settings.defaultReminderTime" type="time" />
            </div>

            <button class="save-setting-btn" @click="saveSettings">
              <i class="bi bi-check-lg"></i>
              Lưu cài đặt
            </button>
          </div>
        </div>

        <!-- Send Demo -->
        <div class="send-demo-card">
          <div class="demo-icon">
            <i class="bi bi-send-check-fill"></i>
          </div>

          <h5>Mô phỏng gửi email</h5>
          <p>
            Nút dưới đây mô phỏng backend kiểm tra các nhắc nhở đã đến giờ và
            cập nhật trạng thái gửi.
          </p>

          <button class="send-demo-btn" @click="simulateSendDueEmails">
            <i class="bi bi-envelope-arrow-up-fill"></i>
            Gửi thử email đến hạn
          </button>
        </div>
      </div>

      <!-- Reminders List -->
      <div class="col-xl-8">
        <div class="content-card">
          <div class="toolbar">
            <div>
              <h5>Danh sách nhắc nhở</h5>
              <p>Quản lý thông báo cho bài tập và kỳ thi của bạn.</p>
            </div>

            <div class="filters">
              <div class="search-box">
                <i class="bi bi-search"></i>
                <input
                  v-model="searchKeyword"
                  type="text"
                  placeholder="Tìm nhắc nhở..."
                />
              </div>

              <select v-model="selectedType">
                <option value="">Tất cả loại</option>
                <option value="TASK">Bài tập</option>
                <option value="EXAM">Lịch thi</option>
              </select>

              <select v-model="selectedStatus">
                <option value="">Tất cả trạng thái</option>
                <option value="PENDING">Chờ gửi</option>
                <option value="SENT">Đã gửi</option>
                <option value="FAILED">Thất bại</option>
                <option value="CANCELLED">Đã hủy</option>
              </select>
            </div>
          </div>

          <!-- Empty -->
          <div v-if="filteredReminders.length === 0" class="empty-state">
            <div class="empty-icon">
              <i class="bi bi-bell-slash"></i>
            </div>

            <h5>Chưa có nhắc nhở phù hợp</h5>
            <p>Hãy tạo nhắc nhở mới cho bài tập hoặc lịch thi.</p>

            <button class="primary-btn" @click="openAddModal">
              <i class="bi bi-plus-lg"></i>
              Tạo nhắc nhở
            </button>
          </div>

          <!-- List -->
          <div v-else class="reminder-list">
            <div
              v-for="reminder in filteredReminders"
              :key="reminder.id"
              class="reminder-card"
              :class="{
                due: isDue(reminder),
                sent: reminder.status === 'SENT',
                cancelled: reminder.status === 'CANCELLED',
              }"
            >
              <div
                class="reminder-type-icon"
                :class="reminder.targetType.toLowerCase()"
              >
                <i
                  :class="
                    reminder.targetType === 'TASK'
                      ? 'bi bi-check2-square'
                      : 'bi bi-calendar-event'
                  "
                ></i>
              </div>

              <div class="reminder-main">
                <div class="reminder-header">
                  <div>
                    <div class="title-row">
                      <h4>{{ getTargetTitle(reminder) }}</h4>

                      <span
                        class="type-badge"
                        :class="reminder.targetType.toLowerCase()"
                      >
                        {{ reminder.targetType === 'TASK' ? 'Bài tập' : 'Lịch thi' }}
                      </span>

                      <span
                        class="status-badge"
                        :class="reminder.status.toLowerCase()"
                      >
                        {{ getStatusText(reminder.status) }}
                      </span>
                    </div>

                    <p class="subject-name">
                      <i class="bi bi-book"></i>
                      {{ getTargetSubjectName(reminder) }}
                    </p>
                  </div>

                  <div class="action-group">
                    <button
                      v-if="reminder.status === 'PENDING'"
                      class="action-btn edit"
                      title="Sửa nhắc nhở"
                      @click="openEditModal(reminder)"
                    >
                      <i class="bi bi-pencil-square"></i>
                    </button>

                    <button
                      v-if="reminder.status === 'PENDING'"
                      class="action-btn cancel"
                      title="Hủy nhắc nhở"
                      @click="cancelReminder(reminder)"
                    >
                      <i class="bi bi-x-circle"></i>
                    </button>

                    <button
                      class="action-btn delete"
                      title="Xóa nhắc nhở"
                      @click="confirmDelete(reminder)"
                    >
                      <i class="bi bi-trash3"></i>
                    </button>
                  </div>
                </div>

                <div class="reminder-details">
                  <div class="detail-item">
                    <i class="bi bi-bell"></i>
                    <div>
                      <small>Thời gian nhắc</small>
                      <p>{{ formatDateTime(reminder.remindAt) }}</p>
                    </div>
                  </div>

                  <div class="detail-item">
                    <i class="bi bi-calendar-check"></i>
                    <div>
                      <small>{{ reminder.targetType === 'TASK' ? 'Deadline' : 'Ngày thi' }}</small>
                      <p>{{ formatDateTime(getTargetDatetime(reminder)) }}</p>
                    </div>
                  </div>

                  <div class="detail-item">
                    <i class="bi bi-envelope"></i>
                    <div>
                      <small>Email nhận</small>
                      <p>{{ reminder.emailTo }}</p>
                    </div>
                  </div>
                </div>

                <div v-if="isDue(reminder)" class="due-alert">
                  <i class="bi bi-exclamation-circle-fill"></i>
                  Nhắc nhở này đã đến thời gian gửi email.
                </div>

                <div v-if="reminder.status === 'SENT'" class="sent-alert">
                  <i class="bi bi-check-circle-fill"></i>
                  Email đã được gửi lúc {{ formatDateTime(reminder.sentAt) }}.
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Email Log -->
        <div class="logs-card">
          <div class="logs-header">
            <div>
              <h5>Lịch sử gửi Email</h5>
              <p>Dữ liệu mô phỏng bảng <code>email_logs</code>.</p>
            </div>

            <span>{{ emailLogs.length }} log</span>
          </div>

          <div v-if="emailLogs.length === 0" class="log-empty">
            Chưa có email nào được gửi.
          </div>

          <div v-else class="log-table-wrapper">
            <table class="log-table">
              <thead>
                <tr>
                  <th>Tiêu đề email</th>
                  <th>Người nhận</th>
                  <th>Thời gian gửi</th>
                  <th>Trạng thái</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="log in sortedEmailLogs" :key="log.id">
                  <td>{{ log.emailSubject }}</td>
                  <td>{{ log.recipientEmail }}</td>
                  <td>{{ formatDateTime(log.sentAt) }}</td>
                  <td>
                    <span
                      class="log-status"
                      :class="log.status.toLowerCase()"
                    >
                      {{ log.status === 'THANH_CONG' ? 'Thành công' : 'Thất bại' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Add/Edit -->
    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-header-custom">
          <div>
            <h4>{{ isEditing ? 'Cập nhật nhắc nhở' : 'Tạo nhắc nhở mới' }}</h4>
            <p>Chọn bài tập hoặc lịch thi cần nhận email nhắc nhở.</p>
          </div>

          <button class="close-btn" @click="closeModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <form @submit.prevent="saveReminder">
          <div class="type-selector">
            <button
              type="button"
              :class="{ active: form.targetType === 'TASK' }"
              @click="changeTargetType('TASK')"
            >
              <i class="bi bi-check2-square"></i>
              Nhắc bài tập
            </button>

            <button
              type="button"
              :class="{ active: form.targetType === 'EXAM' }"
              @click="changeTargetType('EXAM')"
            >
              <i class="bi bi-calendar-event"></i>
              Nhắc lịch thi
            </button>
          </div>

          <div class="form-group">
            <label>
              {{ form.targetType === 'TASK' ? 'Chọn bài tập' : 'Chọn lịch thi' }}
              <span>*</span>
            </label>

            <select
              v-model="form.targetId"
              :class="{ invalid: errors.targetId }"
              @change="setSuggestedTime"
            >
              <option value="">
                {{ form.targetType === 'TASK' ? 'Chọn bài tập' : 'Chọn kỳ thi' }}
              </option>

              <option
                v-for="target in availableTargets"
                :key="target.id"
                :value="String(target.id)"
              >
                {{ target.title }}
              </option>
            </select>

            <small v-if="errors.targetId" class="error-text">
              {{ errors.targetId }}
            </small>
          </div>

          <div v-if="selectedTarget" class="target-preview">
            <div>
              <small>Môn học</small>
              <strong>{{ getSubjectName(selectedTarget.subjectId) }}</strong>
            </div>

            <div>
              <small>
                {{ form.targetType === 'TASK' ? 'Deadline' : 'Ngày thi' }}
              </small>
              <strong>{{ formatDateTime(getSelectedTargetDatetime()) }}</strong>
            </div>
          </div>

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

          <div class="form-group">
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

          <div class="reminder-preview">
            <i class="bi bi-envelope-paper-fill"></i>

            <div>
              <p>Email dự kiến gửi lúc</p>
              <strong>
                {{ form.remindAt ? formatDateTime(form.remindAt) : 'Chưa chọn thời gian' }}
              </strong>
            </div>
          </div>

          <div class="modal-footer-custom">
            <button type="button" class="cancel-btn" @click="closeModal">
              Hủy
            </button>

            <button type="submit" class="save-btn">
              <i class="bi bi-check-lg"></i>
              {{ isEditing ? 'Lưu thay đổi' : 'Tạo nhắc nhở' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Modal -->
    <div v-if="reminderToDelete" class="modal-overlay" @click.self="reminderToDelete = null">
      <div class="delete-modal">
        <div class="delete-icon">
          <i class="bi bi-trash3"></i>
        </div>

        <h4>Xóa nhắc nhở?</h4>
        <p>
          Bạn có chắc muốn xóa nhắc nhở cho
          <strong>{{ getTargetTitle(reminderToDelete) }}</strong> không?
        </p>

        <div class="delete-actions">
          <button class="cancel-btn" @click="reminderToDelete = null">
            Hủy
          </button>

          <button class="confirm-delete-btn" @click="deleteReminder">
            Xóa nhắc nhở
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
import axios from "axios";

const settingStorageKey = 'studymate_notification_settings'
const reminderStorageKey = 'studymate_reminders'
const emailLogStorageKey = 'studymate_email_logs'
const subjectStorageKey = 'studymate_subjects'
const taskStorageKey = 'studymate_tasks'
const examStorageKey = 'studymate_exams'

const toInputDatetime = (dateValue) => {
  const date = new Date(dateValue)
  const offset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - offset).toISOString().slice(0, 16)
}

const createFutureDatetime = (days, hour = 23, minute = 59) => {
  const date = new Date()
  date.setDate(date.getDate() + days)
  date.setHours(hour, minute, 0, 0)
  return toInputDatetime(date)
}

const createPastDatetime = (minutes) => {
  const date = new Date()
  date.setMinutes(date.getMinutes() - minutes)
  return toInputDatetime(date)
}

const createReminderTime = (targetDatetime, daysBefore, time = '08:00') => {
  const date = new Date(targetDatetime)
  date.setDate(date.getDate() - daysBefore)

  const [hour, minute] = time.split(':')
  date.setHours(Number(hour), Number(minute), 0, 0)

  return toInputDatetime(date)
}

const defaultSubjects = [
  { id: 1, name: 'Perl & Python', color: '#6366F1' },
  { id: 2, name: 'System Integration', color: '#0891B2' },
  { id: 3, name: 'Cơ sở dữ liệu', color: '#16A34A' },
  { id: 4, name: 'Lập trình Web', color: '#F97316' },
]

const defaultTasks = [
  {
    id: 1,
    subjectId: '1',
    title: 'Ôn vòng lặp và hàm trong Python',
    deadline: createFutureDatetime(1),
    status: 'CHUA_LAM',
  },
  {
    id: 2,
    subjectId: '1',
    title: 'Xây dựng API FastAPI cho chatbot',
    deadline: createFutureDatetime(3),
    status: 'DANG_LAM',
  },
  {
    id: 3,
    subjectId: '2',
    title: 'Ôn mô hình tích hợp dữ liệu',
    deadline: createFutureDatetime(5),
    status: 'CHUA_LAM',
  },
]

const defaultExams = [
  {
    id: 1,
    subjectId: '1',
    title: 'Thi kết thúc môn Perl & Python',
    examDatetime: createFutureDatetime(10, 7, 0),
  },
  {
    id: 2,
    subjectId: '2',
    title: 'Thi System Integration',
    examDatetime: createFutureDatetime(15, 9, 0),
  },
  {
    id: 3,
    subjectId: '3',
    title: 'Kiểm tra SQL',
    examDatetime: createFutureDatetime(6, 13, 30),
  },
]

const defaultSettings = {
  emailEnabled: true,
  email: 'vothithaingoc072005@gmail.com',
  defaultTaskReminderDays: 1,
  defaultExamReminderDays: 3,
  defaultReminderTime: '08:00',
}

const loadData = (key, defaultData) => {
  const data = localStorage.getItem(key)

  if (data) {
    return JSON.parse(data)
  }

  localStorage.setItem(key, JSON.stringify(defaultData))
  return defaultData
}

const subjects = ref(loadData(subjectStorageKey, defaultSubjects))
const tasks = ref(loadData(taskStorageKey, defaultTasks))
const exams = ref(loadData(examStorageKey, defaultExams))
const settings = ref(loadData(settingStorageKey, defaultSettings))

const defaultReminders = [
  {
    id: 1,
    targetType: 'TASK',
    taskId: 1,
    examId: null,
    remindAt: createReminderTime(defaultTasks[0].deadline, 1),
    emailTo: 'vothithaingoc072005@gmail.com',
    status: 'PENDING',
    sentAt: null,
  },
  {
    id: 2,
    targetType: 'EXAM',
    taskId: null,
    examId: 1,
    remindAt: createReminderTime(defaultExams[0].examDatetime, 3),
    emailTo: 'vothithaingoc072005@gmail.com',
    status: 'PENDING',
    sentAt: null,
  },
  {
    id: 3,
    targetType: 'TASK',
    taskId: 2,
    examId: null,
    remindAt: createPastDatetime(30),
    emailTo: 'vothithaingoc072005@gmail.com',
    status: 'PENDING',
    sentAt: null,
  },
]

const reminders = ref(loadData(reminderStorageKey, defaultReminders))
const emailLogs = ref(loadData(emailLogStorageKey, []))

const searchKeyword = ref('')
const selectedType = ref('')
const selectedStatus = ref('')

const isModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const reminderToDelete = ref(null)
const toastMessage = ref('')

const emptyForm = () => ({
  targetType: 'TASK',
  targetId: '',
  emailTo: settings.value.email,
  remindAt: '',
})

const form = ref(emptyForm())

const errors = ref({
  targetId: '',
  emailTo: '',
  remindAt: '',
})

const pendingCount = computed(() => {
  return reminders.value.filter((reminder) => reminder.status === 'PENDING').length
})

const sentCount = computed(() => {
  return reminders.value.filter((reminder) => reminder.status === 'SENT').length
})

const dueCount = computed(() => {
  return reminders.value.filter((reminder) => isDue(reminder)).length
})

const sortedEmailLogs = computed(() => {
  return [...emailLogs.value].sort(
    (first, second) =>
      new Date(second.sentAt).getTime() - new Date(first.sentAt).getTime(),
  )
})

const availableTargets = computed(() => {
  if (form.value.targetType === 'TASK') {
    return tasks.value.filter((task) => task.status !== 'HOAN_THANH')
  }

  return exams.value.filter(
    (exam) => new Date(exam.examDatetime).getTime() >= new Date().getTime(),
  )
})

const selectedTarget = computed(() => {
  if (!form.value.targetId) {
    return null
  }

  return availableTargets.value.find(
    (target) => String(target.id) === String(form.value.targetId),
  )
})

const filteredReminders = computed(() => {
  const keyword = searchKeyword.value.toLowerCase()

  return [...reminders.value]
    .filter((reminder) => {
      const matchesKeyword =
        getTargetTitle(reminder).toLowerCase().includes(keyword) ||
        getTargetSubjectName(reminder).toLowerCase().includes(keyword) ||
        reminder.emailTo.toLowerCase().includes(keyword)

      const matchesType =
        !selectedType.value || reminder.targetType === selectedType.value

      const matchesStatus =
        !selectedStatus.value || reminder.status === selectedStatus.value

      return matchesKeyword && matchesType && matchesStatus
    })
    .sort(
      (first, second) =>
        new Date(first.remindAt).getTime() - new Date(second.remindAt).getTime(),
    )
})

const persistData = () => {
  localStorage.setItem(settingStorageKey, JSON.stringify(settings.value))
  localStorage.setItem(reminderStorageKey, JSON.stringify(reminders.value))
  localStorage.setItem(emailLogStorageKey, JSON.stringify(emailLogs.value))
}

const getSubjectName = (subjectId) => {
  const subject = subjects.value.find(
    (item) => String(item.id) === String(subjectId),
  )

  return subject ? subject.name : 'Không xác định'
}

const getTarget = (reminder) => {
  if (reminder.targetType === 'TASK') {
    return tasks.value.find(
      (task) => String(task.id) === String(reminder.taskId),
    )
  }

  return exams.value.find(
    (exam) => String(exam.id) === String(reminder.examId),
  )
}

const getTargetTitle = (reminder) => {
  return getTarget(reminder)?.title || 'Nội dung đã bị xóa'
}

const getTargetSubjectName = (reminder) => {
  const target = getTarget(reminder)
  return target ? getSubjectName(target.subjectId) : 'Không xác định'
}

const getTargetDatetime = (reminder) => {
  const target = getTarget(reminder)

  if (!target) {
    return null
  }

  return reminder.targetType === 'TASK'
    ? target.deadline
    : target.examDatetime
}

const getSelectedTargetDatetime = () => {
  if (!selectedTarget.value) {
    return null
  }

  return form.value.targetType === 'TASK'
    ? selectedTarget.value.deadline
    : selectedTarget.value.examDatetime
}

const formatDateTime = (value) => {
  if (!value) {
    return '---'
  }

  return new Date(value).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

const getStatusText = (status) => {
  const statuses = {
    PENDING: 'Chờ gửi',
    SENT: 'Đã gửi',
    FAILED: 'Thất bại',
    CANCELLED: 'Đã hủy',
  }

  return statuses[status] || status
}

const isDue = (reminder) => {
  return (
    reminder.status === 'PENDING' &&
    new Date(reminder.remindAt).getTime() <= new Date().getTime()
  )
}

const showToast = (message) => {
  toastMessage.value = message

  setTimeout(() => {
    toastMessage.value = ''
  }, 2700)
}

const saveSettings = async () => {
  persistData()

  try {
    await axios.post("http://localhost:8000/send-email", {
       email: settings.value.email,
      subject: "StudyMate - Kiem tra email",
      text: "Ban da kich hoat nhan email nhac nho tu StudyMate."
    })

    showToast('Lưu cài đặt và gửi email thành công.')
  } catch (error) {
    console.error(error)
    showToast('Lưu cài đặt thành công nhưng gửi email thất bại.')
  }
}

const resetErrors = () => {
  errors.value = {
    targetId: '',
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

const openEditModal = (reminder) => {
  isEditing.value = true
  editingId.value = reminder.id

  form.value = {
    targetType: reminder.targetType,
    targetId: String(
      reminder.targetType === 'TASK' ? reminder.taskId : reminder.examId,
    ),
    emailTo: reminder.emailTo,
    remindAt: reminder.remindAt,
  }

  resetErrors()
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  resetErrors()
}

const changeTargetType = (type) => {
  form.value.targetType = type
  form.value.targetId = ''
  form.value.remindAt = ''
  resetErrors()
}

const setSuggestedTime = () => {
  if (!selectedTarget.value) {
    form.value.remindAt = ''
    return
  }

  const datetime = getSelectedTargetDatetime()
  const daysBefore =
    form.value.targetType === 'TASK'
      ? settings.value.defaultTaskReminderDays
      : settings.value.defaultExamReminderDays

  form.value.remindAt = createReminderTime(
    datetime,
    daysBefore,
    settings.value.defaultReminderTime,
  )
}

const validateForm = () => {
  resetErrors()
  let valid = true

  if (!form.value.targetId) {
    errors.value.targetId = 'Vui lòng chọn nội dung cần nhắc.'
    valid = false
  }

  if (!form.value.emailTo) {
    errors.value.emailTo = 'Vui lòng nhập email nhận thông báo.'
    valid = false
  }

  if (!form.value.remindAt) {
    errors.value.remindAt = 'Vui lòng chọn thời gian gửi email.'
    valid = false
  }

  if (
    form.value.remindAt &&
    getSelectedTargetDatetime() &&
    new Date(form.value.remindAt).getTime() >=
      new Date(getSelectedTargetDatetime()).getTime()
  ) {
    errors.value.remindAt =
      'Thời gian nhắc phải trước deadline hoặc thời gian thi.'
    valid = false
  }

  const duplicate = reminders.value.some((reminder) => {
    const reminderTargetId =
      reminder.targetType === 'TASK' ? reminder.taskId : reminder.examId

    return (
      reminder.id !== editingId.value &&
      reminder.targetType === form.value.targetType &&
      String(reminderTargetId) === String(form.value.targetId) &&
      reminder.remindAt === form.value.remindAt &&
      reminder.status !== 'CANCELLED'
    )
  })

  if (duplicate) {
    errors.value.remindAt = 'Lịch nhắc này đã tồn tại.'
    valid = false
  }

  return valid
}

const saveReminder = async () => {
  if (!validateForm()) {
    return
  }

  const reminderData = {
  id: isEditing.value ? editingId.value : Date.now(),
  targetType: form.value.targetType,
  taskId: form.value.targetType === 'TASK' ? Number(form.value.targetId) : null,
  examId: form.value.targetType === 'EXAM' ? Number(form.value.targetId) : null,
  remindAt: form.value.remindAt,
  emailTo: form.value.emailTo,
  status: 'PENDING',
  sentAt: null,
}

try {

  await axios.post(
    "http://localhost:8000/api/reminders",
    {
      title: getTargetTitle(reminderData),
      type:
        reminderData.targetType === "TASK"
          ? "Bài tập"
          : "Lịch thi",
      email: reminderData.emailTo,
      remindTime: reminderData.remindAt,
      deadline: getSelectedTargetDatetime()
    }
  );

} catch (error) {

  console.error(error);

}

  if (isEditing.value) {
    const index = reminders.value.findIndex(
      (reminder) => reminder.id === editingId.value,
    )

    reminders.value[index] = reminderData
    showToast('Cập nhật nhắc nhở thành công.')
  } else {
    reminders.value.unshift(reminderData)
    showToast('Tạo nhắc nhở thành công.')
  }

  persistData()
  closeModal()
}

const cancelReminder = (reminder) => {
  reminder.status = 'CANCELLED'
  persistData()
  showToast('Đã hủy nhắc nhở.')
}

const confirmDelete = (reminder) => {
  reminderToDelete.value = reminder
}

const deleteReminder = () => {
  reminders.value = reminders.value.filter(
    (reminder) => reminder.id !== reminderToDelete.value.id,
  )

  persistData()
  reminderToDelete.value = null
  showToast('Đã xóa nhắc nhở.')
}

const simulateSendDueEmails = () => {
  if (!settings.value.emailEnabled) {
    showToast('Bạn đang tắt chức năng nhận email.')
    return
  }

  const dueReminders = reminders.value.filter((reminder) => isDue(reminder))

  if (dueReminders.length === 0) {
    showToast('Hiện chưa có email nào đến thời gian gửi.')
    return
  }

  dueReminders.forEach((reminder) => {
    reminder.status = 'SENT'
    reminder.sentAt = new Date().toISOString()

    emailLogs.value.unshift({
      id: Date.now() + reminder.id,
      reminderId: reminder.id,
      recipientEmail: reminder.emailTo,
      emailSubject: `Nhắc nhở học tập - ${getTargetTitle(reminder)}`,
      emailBody: `Bạn có ${getTargetTitle(reminder)} sắp đến thời gian cần hoàn thành.`,
      status: 'THANH_CONG',
      sentAt: reminder.sentAt,
    })
  })

  persistData()
  showToast(`Đã mô phỏng gửi thành công ${dueReminders.length} email.`)
}
setInterval(async () => {

  try {

    const res = await axios.get(
      "http://localhost:8000/api/reminders"
    );

    const serverReminders = res.data.reminders;

    reminders.value.forEach((reminder) => {

      const found = serverReminders.find(
        (item) =>
          item.email === reminder.emailTo
      );

      if (
        found &&
        found.status === "Đã gửi"
      ) {

        reminder.status = "SENT";
        reminder.sentAt = new Date().toISOString();

      }

    });

    persistData();

  } catch (error) {

    console.log(error);

  }

}, 3000);
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
  height: 108px;
  padding: 21px;
  border-radius: 18px;
  border: 1px solid #edf0f5;
  background: white;
  display: flex;
  align-items: center;
  gap: 17px;
}

.summary-icon {
  width: 55px;
  height: 55px;
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

.summary-icon.orange {
  color: #f97316;
  background: #fff7ed;
}

.summary-icon.red {
  color: #dc2626;
  background: #fef2f2;
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

.settings-card,
.content-card,
.logs-card {
  padding: 24px;
  border: 1px solid #edf0f5;
  border-radius: 19px;
  background: white;
}

.settings-title {
  margin-bottom: 23px;
  display: flex;
  align-items: center;
  gap: 13px;
}

.settings-icon {
  width: 48px;
  height: 48px;
  border-radius: 13px;
  color: #6366f1;
  background: #eef2ff;
  font-size: 23px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.settings-title h5 {
  margin: 0 0 4px;
  font-weight: 700;
}

.settings-title p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

.email-toggle {
  margin-bottom: 22px;
  padding: 15px;
  border-radius: 13px;
  background: #f8faff;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.email-toggle strong {
  display: block;
  margin-bottom: 3px;
  font-size: 14px;
}

.email-toggle small {
  color: #6b7280;
  font-size: 12px;
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

.form-group {
  margin-bottom: 17px;
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
.form-group select {
  width: 100%;
  padding: 12px 13px;
  border: 1px solid #e5e7eb;
  border-radius: 11px;
  outline: none;
  background: white;
}

.form-group input:focus,
.form-group select:focus {
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

.save-setting-btn {
  width: 100%;
  height: 45px;
  border: none;
  border-radius: 11px;
  color: white;
  background: #6366f1;
  font-weight: 600;
}

.send-demo-card {
  margin-top: 22px;
  padding: 24px;
  border-radius: 19px;
  color: white;
  background: linear-gradient(135deg, #111827, #312e81);
}

.demo-icon {
  width: 49px;
  height: 49px;
  margin-bottom: 17px;
  border-radius: 13px;
  background: rgba(255, 255, 255, 0.14);
  font-size: 23px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-demo-card h5 {
  margin: 0 0 9px;
  font-weight: 700;
}

.send-demo-card p {
  margin: 0 0 19px;
  color: #cbd5e1;
  font-size: 14px;
  line-height: 1.6;
}

.send-demo-btn {
  width: 100%;
  height: 45px;
  border: none;
  border-radius: 11px;
  color: #312e81;
  background: white;
  font-weight: 600;
}

.toolbar {
  margin-bottom: 23px;
  display: flex;
  justify-content: space-between;
  gap: 17px;
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
  width: 205px;
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
  min-width: 125px;
  padding: 0 10px;
  border: 1px solid #e5e7eb;
  border-radius: 11px;
  color: #374151;
  background: white;
}

.reminder-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.reminder-card {
  padding: 18px;
  border: 1px solid #edf0f5;
  border-radius: 16px;
  display: flex;
  gap: 15px;
}

.reminder-card.due {
  border-color: #fecaca;
  background: #fffafa;
}

.reminder-card.sent {
  border-color: #dcfce7;
}

.reminder-card.cancelled {
  opacity: 0.66;
}

.reminder-type-icon {
  width: 51px;
  height: 51px;
  flex-shrink: 0;
  border-radius: 13px;
  font-size: 23px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.reminder-type-icon.task {
  color: #6366f1;
  background: #eef2ff;
}

.reminder-type-icon.exam {
  color: #f97316;
  background: #fff7ed;
}

.reminder-main {
  flex: 1;
}

.reminder-header {
  display: flex;
  justify-content: space-between;
  gap: 13px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.title-row h4 {
  margin: 0;
  color: #111827;
  font-size: 16px;
  font-weight: 700;
}

.type-badge,
.status-badge {
  padding: 5px 9px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
}

.type-badge.task {
  color: #4338ca;
  background: #eef2ff;
}

.type-badge.exam {
  color: #c2410c;
  background: #fff7ed;
}

.status-badge.pending {
  color: #ea580c;
  background: #fff7ed;
}

.status-badge.sent {
  color: #15803d;
  background: #f0fdf4;
}

.status-badge.failed {
  color: #dc2626;
  background: #fef2f2;
}

.status-badge.cancelled {
  color: #6b7280;
  background: #f3f4f6;
}

.subject-name {
  margin: 8px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.action-group {
  display: flex;
  gap: 7px;
}

.action-btn {
  width: 35px;
  height: 35px;
  border: none;
  border-radius: 9px;
}

.action-btn.edit {
  color: #ea580c;
  background: #fff7ed;
}

.action-btn.cancel {
  color: #6b7280;
  background: #f3f4f6;
}

.action-btn.delete {
  color: #dc2626;
  background: #fef2f2;
}

.reminder-details {
  margin-top: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 23px;
}

.detail-item {
  min-width: 165px;
  display: flex;
  align-items: center;
  gap: 9px;
}

.detail-item > i {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  color: #6366f1;
  background: #eef2ff;
  display: flex;
  justify-content: center;
  align-items: center;
}

.detail-item small {
  display: block;
  margin-bottom: 3px;
  color: #6b7280;
}

.detail-item p {
  margin: 0;
  color: #111827;
  font-size: 13px;
  font-weight: 500;
}

.due-alert,
.sent-alert {
  margin-top: 15px;
  padding: 10px 13px;
  border-radius: 9px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 7px;
}

.due-alert {
  color: #b91c1c;
  background: #fef2f2;
}

.sent-alert {
  color: #15803d;
  background: #f0fdf4;
}

.logs-card {
  margin-top: 22px;
}

.logs-header {
  margin-bottom: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logs-header h5 {
  margin: 0 0 4px;
  font-weight: 700;
}

.logs-header p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

.logs-header code {
  color: #4338ca;
}

.logs-header span {
  padding: 6px 11px;
  border-radius: 20px;
  color: #4338ca;
  background: #eef2ff;
  font-size: 12px;
  font-weight: 600;
}

.log-empty {
  padding: 30px 0;
  color: #6b7280;
  text-align: center;
}

.log-table {
  width: 100%;
  border-collapse: collapse;
}

.log-table th {
  padding: 12px 13px;
  color: #6b7280;
  background: #f8fafc;
  font-size: 13px;
  text-align: left;
}

.log-table td {
  padding: 13px;
  border-bottom: 1px solid #f1f5f9;
  color: #374151;
  font-size: 13px;
}

.log-status {
  padding: 5px 9px;
  border-radius: 20px;
  font-weight: 600;
}

.log-status.thanh_cong {
  color: #15803d;
  background: #f0fdf4;
}

.log-status.that_bai {
  color: #dc2626;
  background: #fef2f2;
}

.empty-state {
  padding: 58px 20px;
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
  width: 590px;
  max-width: 100%;
  max-height: 94vh;
  overflow-y: auto;
  padding: 27px;
  border-radius: 20px;
  background: white;
}

.modal-header-custom {
  margin-bottom: 22px;
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

.type-selector {
  margin-bottom: 20px;
  display: flex;
  gap: 11px;
}

.type-selector button {
  flex: 1;
  height: 57px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  color: #374151;
  background: white;
  font-weight: 600;
}

.type-selector button i {
  margin-right: 7px;
}

.type-selector button.active {
  border-color: #6366f1;
  color: #4338ca;
  background: #eef2ff;
}

.target-preview {
  margin-bottom: 18px;
  padding: 14px;
  border-radius: 12px;
  background: #f8faff;
  display: flex;
  gap: 28px;
}

.target-preview small {
  display: block;
  margin-bottom: 5px;
  color: #6b7280;
}

.target-preview strong {
  color: #111827;
  font-size: 13px;
}

.reminder-preview {
  margin-bottom: 23px;
  padding: 14px;
  border: 1px solid #e0e7ff;
  border-radius: 12px;
  background: #f8faff;
  display: flex;
  align-items: center;
  gap: 13px;
}

.reminder-preview i {
  width: 44px;
  height: 44px;
  border-radius: 11px;
  color: #6366f1;
  background: #eef2ff;
  font-size: 22px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.reminder-preview p {
  margin: 0 0 4px;
  color: #6b7280;
  font-size: 12px;
}

.reminder-preview strong {
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
  .reminder-header,
  .reminder-details,
  .target-preview {
    flex-direction: column;
    align-items: flex-start;
  }

  .filters,
  .search-box,
  .filters select {
    width: 100%;
  }

  .reminder-card {
    flex-direction: column;
  }

  .log-table-wrapper {
    overflow-x: auto;
  }
}
</style>