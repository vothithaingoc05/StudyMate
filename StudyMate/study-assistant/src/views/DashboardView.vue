<template>
  <div class="dashboard-page">
    <!-- Hero -->
    <section class="hero-card">
      <div class="hero-content">
        <div class="welcome-badge">
          <i class="bi bi-stars"></i>
          StudyMate AI Assistant
        </div>

        <p class="hello">Xin chào, Thái Ngọc 👋</p>
        <h1>Học tập thông minh hơn mỗi ngày</h1>

        <p class="hero-description">
          Bạn có
          <strong>{{ urgentTasks.length }} công việc cần ưu tiên</strong>
          và
          <strong>{{ eventsThisWeek }} lịch học hoặc kỳ thi</strong>
          trong 7 ngày tới.
        </p>

        <div class="hero-actions">
          <RouterLink to="/ke-hoach-on-tap" class="hero-primary-btn">
            <i class="bi bi-calendar-plus"></i>
            Tạo kế hoạch học
          </RouterLink>

          <RouterLink to="/chatbot" class="hero-secondary-btn">
            <i class="bi bi-robot"></i>
            Hỏi StudyMate AI
          </RouterLink>
        </div>
      </div>

      <div class="hero-side">
        <div class="progress-ring">
          <div class="ring-value">
            <strong>{{ overallProgress }}%</strong>
            <span>Tiến độ</span>
          </div>
        </div>

        <div class="today-note">
          <i class="bi bi-lightning-charge-fill"></i>
          <div>
            <small>Hôm nay</small>
            <strong>{{ todayStudyPlans }} lịch học cần theo dõi</strong>
          </div>
        </div>
      </div>
    </section>

    <!-- Summary Cards -->
    <section class="row g-4 summary-section">
      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon purple">
            <i class="bi bi-book-fill"></i>
          </div>

          <div class="summary-info">
            <p>Môn học</p>
            <h3>{{ subjects.length }}</h3>
            <small>{{ subjectsWithDocuments }} môn đã có tài liệu</small>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon orange">
            <i class="bi bi-check2-square"></i>
          </div>

          <div class="summary-info">
            <p>Bài tập chưa hoàn thành</p>
            <h3>{{ unfinishedTasks }}</h3>
            <small class="danger-text">
              {{ nearDeadlineTasks }} bài gần deadline
            </small>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon blue">
            <i class="bi bi-calendar-event-fill"></i>
          </div>

          <div class="summary-info">
            <p>Lịch thi sắp tới</p>
            <h3>{{ upcomingExams.length }}</h3>
            <small class="blue-text">{{ nearestExamText }}</small>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon green">
            <i class="bi bi-file-earmark-text-fill"></i>
          </div>

          <div class="summary-info">
            <p>Tài liệu học tập</p>
            <h3>{{ documents.length }}</h3>
            <small class="green-text">{{ totalChunks }} đoạn cho chatbot</small>
          </div>
        </div>
      </div>
    </section>

    <!-- Charts -->
    <section class="row g-4 dashboard-row">
      <div class="col-xl-5">
        <div class="content-card chart-card">
          <div class="card-heading">
            <div>
              <h5>Trạng thái bài tập</h5>
              <p>Tỷ lệ hoàn thành công việc hiện tại</p>
            </div>

            <span class="live-badge">
              <i class="bi bi-circle-fill"></i>
              Cập nhật
            </span>
          </div>

          <div class="doughnut-wrapper">
            <Doughnut :data="taskStatusChartData" :options="doughnutOptions" />

            <div class="chart-center">
              <strong>{{ tasks.length }}</strong>
              <span>Bài tập</span>
            </div>
          </div>

          <div class="legend-grid">
            <div class="legend-item">
              <span class="legend-dot not-started"></span>
              <div>
                <small>Chưa làm</small>
                <strong>{{ taskCounts.notStarted }}</strong>
              </div>
            </div>

            <div class="legend-item">
              <span class="legend-dot doing"></span>
              <div>
                <small>Đang làm</small>
                <strong>{{ taskCounts.doing }}</strong>
              </div>
            </div>

            <div class="legend-item">
              <span class="legend-dot completed"></span>
              <div>
                <small>Hoàn thành</small>
                <strong>{{ taskCounts.completed }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-7">
        <div class="content-card chart-card">
          <div class="card-heading">
            <div>
              <h5>Khối lượng công việc theo môn</h5>
              <p>Số bài tập chưa hoàn thành cần ưu tiên</p>
            </div>

            <RouterLink to="/bai-tap" class="view-link">
              Xem bài tập
              <i class="bi bi-arrow-right"></i>
            </RouterLink>
          </div>

          <div class="bar-wrapper">
            <Bar :data="subjectTaskChartData" :options="barOptions" />
          </div>
        </div>
      </div>
    </section>

    <!-- Bottom Dashboard -->
    <section class="row g-4 dashboard-row">
      <!-- Priority Tasks -->
      <div class="col-xl-7">
        <div class="content-card">
          <div class="card-heading">
            <div>
              <h5>Công việc cần ưu tiên</h5>
              <p>Xếp hạng theo deadline, độ khó và mức độ quan trọng</p>
            </div>

            <RouterLink to="/bai-tap" class="view-link">
              Xem tất cả
              <i class="bi bi-arrow-right"></i>
            </RouterLink>
          </div>

          <div v-if="urgentTasks.length === 0" class="small-empty">
            <i class="bi bi-check-circle"></i>
            Bạn chưa có bài tập cần ưu tiên.
          </div>

          <div v-else class="priority-list">
            <div
              v-for="task in urgentTasks.slice(0, 4)"
              :key="task.id"
              class="priority-item"
            >
              <div class="priority-rank">
                {{ task.rank }}
              </div>

              <div class="priority-content">
                <div class="priority-title">
                  <p>{{ task.title }}</p>
                  <span
                    class="priority-badge"
                    :class="task.priority.className"
                  >
                    {{ task.priority.label }}
                  </span>
                </div>

                <div class="priority-meta">
                  <span>
                    <i class="bi bi-book"></i>
                    {{ getSubjectName(task.subjectId) }}
                  </span>

                  <span>
                    <i class="bi bi-clock"></i>
                    {{ remainingText(task) }}
                  </span>

                  <span>
                    <i class="bi bi-stars"></i>
                    Điểm {{ task.priority.score }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Events -->
      <div class="col-xl-5">
        <div class="content-card">
          <div class="card-heading">
            <div>
              <h5>Lịch sắp tới</h5>
              <p>Kế hoạch học và lịch thi gần nhất</p>
            </div>
          </div>

          <div v-if="upcomingEvents.length === 0" class="small-empty">
            <i class="bi bi-calendar-check"></i>
            Chưa có lịch sắp tới.
          </div>

          <div v-else class="event-list">
            <div
              v-for="event in upcomingEvents.slice(0, 4)"
              :key="`${event.type}-${event.id}`"
              class="event-item"
            >
              <div class="event-date" :class="event.type.toLowerCase()">
                <strong>{{ getDay(event.datetime) }}</strong>
                <small>{{ getMonth(event.datetime) }}</small>
              </div>

              <div class="event-content">
                <div class="event-title">
                  <p>{{ event.title }}</p>
                  <span :class="event.type.toLowerCase()">
                    {{ event.type === 'EXAM' ? 'Thi' : 'Học' }}
                  </span>
                </div>

                <small>
                  {{ formatEventTime(event.datetime) }} ·
                  {{ getSubjectName(event.subjectId) }}
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Progress + Quick Tools -->
    <section class="row g-4 dashboard-row">
      <div class="col-xl-7">
        <div class="content-card">
          <div class="card-heading">
            <div>
              <h5>Tiến độ theo môn học</h5>
              <p>Tỷ lệ bài tập đã hoàn thành của từng môn</p>
            </div>
          </div>

          <div v-if="subjectProgress.length === 0" class="small-empty">
            Chưa có dữ liệu tiến độ.
          </div>

          <div v-else class="subject-progress-list">
            <div
              v-for="subject in subjectProgress"
              :key="subject.id"
              class="subject-progress-item"
            >
              <div class="subject-progress-heading">
                <div class="subject-label">
                  <span :style="{ backgroundColor: subject.color }"></span>
                  <strong>{{ subject.name }}</strong>
                </div>

                <small>
                  {{ subject.completed }}/{{ subject.total }} bài hoàn thành
                  · <strong>{{ subject.percent }}%</strong>
                </small>
              </div>

              <div class="progress-track">
                <div
                  class="progress-fill"
                  :style="{
                    width: `${subject.percent}%`,
                    backgroundColor: subject.color,
                  }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-5">
        <div class="quick-tools-grid">
          <RouterLink to="/chatbot" class="tool-card ai-tool">
            <div class="tool-icon">
              <i class="bi bi-robot"></i>
            </div>

            <div>
              <h5>Hỏi StudyMate AI</h5>
              <p>Giải thích bài học dựa trên tài liệu đã lưu.</p>
            </div>

            <i class="bi bi-arrow-up-right arrow-icon"></i>
          </RouterLink>

          <RouterLink to="/nhac-nho-email" class="tool-card email-tool">
            <div class="tool-icon">
              <i class="bi bi-bell-fill"></i>
            </div>

            <div>
              <h5>Nhắc nhở Email</h5>
              <p>
                {{ pendingReminders }} thông báo đang chờ gửi đến
                vothithaingoc072005@gmail.com.
              </p>
            </div>

            <i class="bi bi-arrow-up-right arrow-icon"></i>
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js'

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
)

const subjects = ref([])
const tasks = ref([])
const exams = ref([])
const studyPlans = ref([])
const documents = ref([])
const reminders = ref([])

const getStorageData = (key) => {
  try {
    return JSON.parse(localStorage.getItem(key) || '[]')
  } catch (error) {
    console.error(`Không thể đọc dữ liệu ${key}`, error)
    return []
  }
}

const loadDashboardData = () => {
  subjects.value = getStorageData('studymate_subjects')
  tasks.value = getStorageData('studymate_tasks')
  exams.value = getStorageData('studymate_exams')
  studyPlans.value = getStorageData('studymate_study_plans')
  documents.value = getStorageData('studymate_documents')
  reminders.value = getStorageData('studymate_reminders')
}

const unfinishedTasks = computed(() => {
  return tasks.value.filter((task) => task.status !== 'HOAN_THANH').length
})

const taskCounts = computed(() => ({
  notStarted: tasks.value.filter((task) => task.status === 'CHUA_LAM').length,
  doing: tasks.value.filter((task) => task.status === 'DANG_LAM').length,
  completed: tasks.value.filter((task) => task.status === 'HOAN_THANH').length,
}))

const nearDeadlineTasks = computed(() => {
  return tasks.value.filter((task) => {
    const days = getDaysRemaining(task.deadline)

    return task.status !== 'HOAN_THANH' && days >= 0 && days <= 3
  }).length
})

const upcomingExams = computed(() => {
  return [...exams.value]
    .filter((exam) => new Date(exam.examDatetime).getTime() >= Date.now())
    .sort(
      (first, second) =>
        new Date(first.examDatetime).getTime() -
        new Date(second.examDatetime).getTime(),
    )
})

const nearestExamText = computed(() => {
  if (upcomingExams.value.length === 0) {
    return 'Chưa có lịch thi'
  }

  return `Gần nhất: ${formatShortDate(upcomingExams.value[0].examDatetime)}`
})

const totalChunks = computed(() => {
  return documents.value.reduce((total, document) => {
    return total + Number(document.chunks?.length || 0)
  }, 0)
})

const subjectsWithDocuments = computed(() => {
  return new Set(
    documents.value.map((document) => String(document.subjectId)),
  ).size
})

const overallProgress = computed(() => {
  if (tasks.value.length === 0) {
    return 0
  }

  return Math.round((taskCounts.value.completed / tasks.value.length) * 100)
})

const todayStudyPlans = computed(() => {
  const today = toDateInput(new Date())

  return studyPlans.value.filter(
    (plan) =>
      plan.studyDate === today &&
      plan.status !== 'DA_HOAN_THANH',
  ).length
})

const pendingReminders = computed(() => {
  return reminders.value.filter((reminder) => reminder.status === 'PENDING').length
})

const eventsThisWeek = computed(() => {
  const nextSevenDays = Date.now() + 7 * 24 * 60 * 60 * 1000

  return upcomingEvents.value.filter((event) => {
    const time = new Date(event.datetime).getTime()
    return time <= nextSevenDays
  }).length
})

const taskStatusChartData = computed(() => ({
  labels: ['Chưa làm', 'Đang làm', 'Hoàn thành'],
  datasets: [
    {
      data: [
        taskCounts.value.notStarted,
        taskCounts.value.doing,
        taskCounts.value.completed,
      ],
      backgroundColor: ['#f97316', '#6366f1', '#22c55e'],
      borderWidth: 0,
      hoverOffset: 5,
    },
  ],
}))

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '72%',
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      displayColors: false,
      callbacks: {
        label(context) {
          return `${context.label}: ${context.raw} bài`
        },
      },
    },
  },
}

const subjectTaskChartData = computed(() => {
  const labels = subjects.value.map((subject) => subject.name)

  const unfinishedData = subjects.value.map((subject) => {
    return tasks.value.filter(
      (task) =>
        String(task.subjectId) === String(subject.id) &&
        task.status !== 'HOAN_THANH',
    ).length
  })

  const completedData = subjects.value.map((subject) => {
    return tasks.value.filter(
      (task) =>
        String(task.subjectId) === String(subject.id) &&
        task.status === 'HOAN_THANH',
    ).length
  })

  return {
    labels,
    datasets: [
      {
        label: 'Chưa hoàn thành',
        data: unfinishedData,
        backgroundColor: '#6366f1',
        borderRadius: 7,
        barThickness: 22,
      },
      {
        label: 'Đã hoàn thành',
        data: completedData,
        backgroundColor: '#dbeafe',
        borderRadius: 7,
        barThickness: 22,
      },
    ],
  }
})

const barOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        boxWidth: 10,
        boxHeight: 10,
        usePointStyle: true,
        padding: 20,
        color: '#6b7280',
      },
    },
  },
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        color: '#6b7280',
      },
      border: {
        display: false,
      },
    },
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1,
        color: '#6b7280',
      },
      grid: {
        color: '#f1f5f9',
      },
      border: {
        display: false,
      },
    },
  },
}

const urgentTasks = computed(() => {
  return tasks.value
    .filter((task) => task.status !== 'HOAN_THANH')
    .map((task) => ({
      ...task,
      priority: getPriority(task),
    }))
    .sort(
      (first, second) =>
        Number(second.priority.score) - Number(first.priority.score),
    )
    .map((task, index) => ({
      ...task,
      rank: index + 1,
    }))
})

const upcomingEvents = computed(() => {
  const planEvents = studyPlans.value
    .filter((plan) => {
      const datetime = `${plan.studyDate}T${plan.startTime || '00:00'}`
      return (
        plan.status !== 'DA_HOAN_THANH' &&
        new Date(datetime).getTime() >= Date.now()
      )
    })
    .map((plan) => ({
      id: plan.id,
      type: 'STUDY',
      title: plan.title,
      subjectId: plan.subjectId,
      datetime: `${plan.studyDate}T${plan.startTime || '00:00'}`,
    }))

  const examEvents = exams.value
    .filter((exam) => new Date(exam.examDatetime).getTime() >= Date.now())
    .map((exam) => ({
      id: exam.id,
      type: 'EXAM',
      title: exam.title,
      subjectId: exam.subjectId,
      datetime: exam.examDatetime,
    }))

  return [...planEvents, ...examEvents].sort(
    (first, second) =>
      new Date(first.datetime).getTime() -
      new Date(second.datetime).getTime(),
  )
})

const subjectProgress = computed(() => {
  return subjects.value
    .map((subject) => {
      const subjectTasks = tasks.value.filter(
        (task) => String(task.subjectId) === String(subject.id),
      )

      const completed = subjectTasks.filter(
        (task) => task.status === 'HOAN_THANH',
      ).length

      const total = subjectTasks.length

      return {
        id: subject.id,
        name: subject.name,
        color: subject.color || '#6366F1',
        completed,
        total,
        percent: total === 0 ? 0 : Math.round((completed / total) * 100),
      }
    })
    .filter((subject) => subject.total > 0)
})

const getSubjectName = (subjectId) => {
  const subject = subjects.value.find(
    (item) => String(item.id) === String(subjectId),
  )

  return subject ? subject.name : 'Không xác định'
}

const getDaysRemaining = (datetime) => {
  if (!datetime) {
    return 999
  }

  const difference = new Date(datetime).getTime() - Date.now()
  return Math.ceil(difference / (1000 * 60 * 60 * 24))
}

const remainingText = (task) => {
  const days = getDaysRemaining(task.deadline)

  if (days < 0) {
    return `Quá hạn ${Math.abs(days)} ngày`
  }

  if (days === 0) {
    return 'Hạn hôm nay'
  }

  if (days === 1) {
    return 'Hạn ngày mai'
  }

  return `Còn ${days} ngày`
}

const getPriority = (task) => {
  const days = getDaysRemaining(task.deadline)
  const importance = Number(task.importance || 1)
  const difficulty = Number(task.difficulty || 1)

  let score

  if (days < 0) {
    score = (importance * 2 + difficulty) * 10

    return {
      score: score.toFixed(2),
      label: 'Quá hạn',
      className: 'overdue',
    }
  }

  score = (importance * 2 + difficulty) / Math.max(days, 1)

  if (days <= 1) {
    return {
      score: score.toFixed(2),
      label: 'Rất cao',
      className: 'very-high',
    }
  }

  if (days <= 3) {
    return {
      score: score.toFixed(2),
      label: 'Cao',
      className: 'high',
    }
  }

  if (score >= 2) {
    return {
      score: score.toFixed(2),
      label: 'Trung bình',
      className: 'medium',
    }
  }

  return {
    score: score.toFixed(2),
    label: 'Thấp',
    className: 'low',
  }
}

const toDateInput = (date) => {
  const offset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - offset).toISOString().slice(0, 10)
}

const formatShortDate = (datetime) => {
  return new Date(datetime).toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
  })
}

const formatEventTime = (datetime) => {
  return new Date(datetime).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
  })
}

const getDay = (datetime) => {
  return new Date(datetime).toLocaleDateString('vi-VN', {
    day: '2-digit',
  })
}

const getMonth = (datetime) => {
  const month = new Date(datetime).getMonth() + 1
  return `TH${month}`
}

onMounted(() => {
  loadDashboardData()
  window.addEventListener('focus', loadDashboardData)
  window.addEventListener('storage', loadDashboardData)
})

onUnmounted(() => {
  window.removeEventListener('focus', loadDashboardData)
  window.removeEventListener('storage', loadDashboardData)
})
</script>

<style scoped>
.dashboard-page {
  padding-bottom: 28px;
}

.hero-card {
  position: relative;
  overflow: hidden;
  min-height: 244px;
  padding: 32px 38px;
  border-radius: 27px;
  color: white;
  background:
    radial-gradient(circle at 86% 12%, rgba(255, 255, 255, 0.24), transparent 22%),
    linear-gradient(125deg, #312e81 0%, #4f46e5 48%, #7c3aed 100%);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 32px;
}

.hero-card::after {
  content: '';
  position: absolute;
  right: -85px;
  bottom: -120px;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.hero-content {
  position: relative;
  z-index: 1;
}

.welcome-badge {
  width: fit-content;
  margin-bottom: 14px;
  padding: 7px 13px;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.13);
  font-size: 12px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 7px;
}

.hello {
  margin: 0 0 7px;
  color: #e0e7ff;
  font-size: 15px;
}

.hero-content h1 {
  margin: 0 0 11px;
  font-size: 31px;
  font-weight: 750;
}

.hero-description {
  margin: 0 0 23px;
  max-width: 560px;
  color: #e0e7ff;
  font-size: 15px;
}

.hero-description strong {
  color: white;
}

.hero-actions {
  display: flex;
  gap: 11px;
}

.hero-primary-btn,
.hero-secondary-btn {
  height: 47px;
  padding: 0 18px;
  border-radius: 12px;
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.hero-primary-btn {
  color: #4338ca;
  background: white;
}

.hero-primary-btn:hover {
  color: #3730a3;
}

.hero-secondary-btn {
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.32);
  background: rgba(255, 255, 255, 0.09);
}

.hero-secondary-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.17);
}

.hero-side {
  position: relative;
  z-index: 1;
  min-width: 236px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.progress-ring {
  width: 121px;
  height: 121px;
  border-radius: 50%;
  background:
    radial-gradient(closest-side, #5448da 76%, transparent 77% 100%),
    conic-gradient(#ffffff calc(v-bind(overallProgress) * 1%), rgba(255, 255, 255, 0.22) 0);
  display: flex;
  align-items: center;
  justify-content: center;
}

.ring-value {
  display: flex;
  flex-direction: column;
  text-align: center;
}

.ring-value strong {
  font-size: 27px;
}

.ring-value span {
  color: #e0e7ff;
  font-size: 12px;
}

.today-note {
  padding: 11px 14px;
  border-radius: 13px;
  background: rgba(255, 255, 255, 0.13);
  display: flex;
  align-items: center;
  gap: 10px;
}

.today-note i {
  color: #fde68a;
  font-size: 22px;
}

.today-note small {
  display: block;
  color: #e0e7ff;
  font-size: 11px;
}

.today-note strong {
  display: block;
  font-size: 13px;
}

.summary-section,
.dashboard-row {
  margin-top: 2px;
  padding-top: 22px;
}

.summary-card,
.content-card {
  border: 1px solid #edf0f5;
  border-radius: 20px;
  background: white;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.035);
}

.summary-card {
  min-height: 116px;
  padding: 21px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.summary-icon {
  width: 55px;
  height: 55px;
  border-radius: 16px;
  flex-shrink: 0;
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

.summary-icon.blue {
  color: #2563eb;
  background: #eff6ff;
}

.summary-icon.green {
  color: #16a34a;
  background: #f0fdf4;
}

.summary-info p {
  margin: 0 0 4px;
  color: #6b7280;
  font-size: 13px;
}

.summary-info h3 {
  margin: 0 0 4px;
  color: #111827;
  font-size: 28px;
  font-weight: 700;
}

.summary-info small {
  color: #6b7280;
  font-size: 12px;
}

.summary-info .danger-text {
  color: #dc2626;
}

.summary-info .blue-text {
  color: #2563eb;
}

.summary-info .green-text {
  color: #16a34a;
}

.content-card {
  height: 100%;
  padding: 23px;
}

.chart-card {
  min-height: 375px;
}

.card-heading {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 14px;
}

.card-heading h5 {
  margin: 0 0 5px;
  color: #111827;
  font-size: 17px;
  font-weight: 700;
}

.card-heading p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

.live-badge {
  padding: 6px 11px;
  border-radius: 22px;
  color: #15803d;
  background: #f0fdf4;
  font-size: 11px;
  font-weight: 700;
}

.live-badge i {
  margin-right: 5px;
  font-size: 8px;
}

.view-link {
  color: #6366f1;
  text-decoration: none;
  font-size: 13px;
  font-weight: 600;
}

.view-link i {
  margin-left: 4px;
}

.doughnut-wrapper {
  position: relative;
  height: 210px;
}

.chart-center {
  position: absolute;
  inset: 0;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.chart-center strong {
  color: #111827;
  font-size: 29px;
}

.chart-center span {
  color: #6b7280;
  font-size: 12px;
}

.legend-grid {
  margin-top: 12px;
  display: flex;
  justify-content: center;
  gap: 24px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}

.legend-dot.not-started {
  background: #f97316;
}

.legend-dot.doing {
  background: #6366f1;
}

.legend-dot.completed {
  background: #22c55e;
}

.legend-item small {
  display: block;
  color: #6b7280;
  font-size: 11px;
}

.legend-item strong {
  color: #111827;
  font-size: 15px;
}

.bar-wrapper {
  height: 287px;
}

.priority-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.priority-item {
  padding: 15px;
  border: 1px solid #f1f5f9;
  border-radius: 15px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.priority-item:hover {
  border-color: #e0e7ff;
  background: #fafaff;
}

.priority-rank {
  width: 37px;
  height: 37px;
  border-radius: 11px;
  color: #4338ca;
  background: #eef2ff;
  font-weight: 700;
  display: flex;
  justify-content: center;
  align-items: center;
}

.priority-content {
  flex: 1;
}

.priority-title {
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.priority-title p {
  margin: 0;
  color: #111827;
  font-weight: 600;
}

.priority-badge {
  padding: 5px 11px;
  border-radius: 24px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}

.priority-badge.overdue,
.priority-badge.very-high {
  color: #dc2626;
  background: #fef2f2;
}

.priority-badge.high {
  color: #ea580c;
  background: #fff7ed;
}

.priority-badge.medium {
  color: #2563eb;
  background: #eff6ff;
}

.priority-badge.low {
  color: #6b7280;
  background: #f3f4f6;
}

.priority-meta {
  color: #6b7280;
  font-size: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.priority-meta i {
  margin-right: 4px;
}

.event-list {
  display: flex;
  flex-direction: column;
  gap: 13px;
}

.event-item {
  padding: 12px;
  border-radius: 14px;
  background: #f8fafc;
  display: flex;
  align-items: center;
  gap: 13px;
}

.event-date {
  width: 53px;
  height: 55px;
  flex-shrink: 0;
  border-radius: 13px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  line-height: 20px;
}

.event-date.exam {
  color: #c2410c;
  background: #fff7ed;
}

.event-date.study {
  color: #4338ca;
  background: #eef2ff;
}

.event-date strong {
  font-size: 18px;
}

.event-date small {
  font-size: 11px;
  font-weight: 700;
}

.event-content {
  flex: 1;
}

.event-title {
  display: flex;
  gap: 8px;
  align-items: center;
}

.event-title p {
  margin: 0 0 4px;
  color: #111827;
  font-size: 14px;
  font-weight: 600;
}

.event-title span {
  padding: 3px 7px;
  margin-bottom: 4px;
  border-radius: 18px;
  font-size: 10px;
  font-weight: 700;
}

.event-title span.exam {
  color: #c2410c;
  background: #ffedd5;
}

.event-title span.study {
  color: #4338ca;
  background: #e0e7ff;
}

.event-content small {
  color: #6b7280;
  font-size: 12px;
}

.subject-progress-list {
  display: flex;
  flex-direction: column;
  gap: 19px;
}

.subject-progress-heading {
  margin-bottom: 9px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.subject-label {
  display: flex;
  align-items: center;
  gap: 9px;
}

.subject-label span {
  width: 9px;
  height: 31px;
  border-radius: 20px;
}

.subject-label strong {
  color: #111827;
  font-size: 14px;
}

.subject-progress-heading small {
  color: #6b7280;
}

.progress-track {
  width: 100%;
  height: 8px;
  border-radius: 30px;
  background: #f1f5f9;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 30px;
  transition: width 0.3s;
}

.quick-tools-grid {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tool-card {
  position: relative;
  flex: 1;
  min-height: 136px;
  padding: 22px;
  border-radius: 20px;
  color: white;
  text-decoration: none;
  display: flex;
  align-items: flex-start;
  gap: 15px;
}

.tool-card:hover {
  color: white;
  transform: translateY(-2px);
}

.ai-tool {
  background: linear-gradient(135deg, #111827, #312e81);
}

.email-tool {
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
}

.tool-icon {
  width: 49px;
  height: 49px;
  flex-shrink: 0;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.16);
  font-size: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.tool-card h5 {
  margin: 2px 0 8px;
  font-weight: 700;
}

.tool-card p {
  margin: 0;
  padding-right: 22px;
  color: #e0e7ff;
  font-size: 13px;
  line-height: 1.55;
}

.arrow-icon {
  position: absolute;
  right: 18px;
  top: 19px;
  font-size: 18px;
}

.small-empty {
  min-height: 146px;
  color: #6b7280;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 9px;
}

.small-empty i {
  color: #6366f1;
  font-size: 21px;
}

@media (max-width: 992px) {
  .hero-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .hero-side {
    width: 100%;
    flex-direction: row;
    justify-content: flex-start;
  }
}

@media (max-width: 768px) {
  .hero-card {
    padding: 27px 23px;
  }

  .hero-content h1 {
    font-size: 26px;
  }

  .hero-actions,
  .priority-title,
  .subject-progress-heading {
    flex-direction: column;
    align-items: flex-start;
  }

  .legend-grid {
    gap: 13px;
  }
}
</style>