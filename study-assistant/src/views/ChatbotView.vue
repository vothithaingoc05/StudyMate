<template>
  <div class="chatbot-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h2>Chatbot hỏi đáp</h2>
        <p>Đặt câu hỏi dựa trên tài liệu học tập bạn đã lưu trong hệ thống.</p>
      </div>

      <button class="primary-btn" @click="createNewChat">
        <i class="bi bi-plus-lg"></i>
        Cuộc trò chuyện mới
      </button>
    </div>

    <!-- Summary -->
    <div class="row g-4 mb-4">
      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon purple">
            <i class="bi bi-chat-dots-fill"></i>
          </div>

          <div>
            <p>Cuộc trò chuyện</p>
            <h3>{{ sessions.length }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon blue">
            <i class="bi bi-question-circle-fill"></i>
          </div>

          <div>
            <p>Câu hỏi đã gửi</p>
            <h3>{{ totalQuestions }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon green">
            <i class="bi bi-file-earmark-text-fill"></i>
          </div>

          <div>
            <p>Tài liệu khả dụng</p>
            <h3>{{ documents.length }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon orange">
            <i class="bi bi-stars"></i>
          </div>

          <div>
            <p>Lượt tìm nguồn</p>
            <h3>{{ sources.length }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Chat Layout -->
    <div class="chat-layout">
      <!-- History Sidebar -->
      <aside class="history-panel">
        <div class="history-header">
          <h5>Lịch sử hỏi đáp</h5>
          <button class="small-add-btn" @click="createNewChat">
            <i class="bi bi-plus-lg"></i>
          </button>
        </div>

        <div class="history-list">
          <button
            v-for="session in sortedSessions"
            :key="session.id"
            class="history-item"
            :class="{ active: session.id === currentSessionId }"
            @click="selectSession(session)"
          >
            <div class="history-icon">
              <i class="bi bi-chat-left-text"></i>
            </div>

            <div class="history-content">
              <p>{{ session.title }}</p>
              <small>
                {{ getSubjectName(session.subjectId) }} ·
                {{ formatShortDate(session.updatedAt) }}
              </small>
            </div>

            <span
              class="delete-session"
              title="Xóa cuộc trò chuyện"
              @click.stop="deleteSession(session.id)"
            >
              <i class="bi bi-trash3"></i>
            </span>
          </button>
        </div>
      </aside>

      <!-- Chat Area -->
      <section class="chat-panel">
        <div class="chat-header">
          <div class="chat-title">
            <div class="bot-avatar">
              <i class="bi bi-robot"></i>
            </div>

            <div>
              <h5>StudyMate AI</h5>
              <p>
                <span class="online-dot"></span>
                Mô phỏng trả lời theo tài liệu đã lưu
              </p>
            </div>
          </div>

          <div class="subject-select">
            <label>Môn học</label>
            <select v-model="selectedSubjectId" @change="handleSubjectChange">
              <option
                v-for="subject in subjects"
                :key="subject.id"
                :value="String(subject.id)"
              >
                {{ subject.name }}
              </option>
            </select>
          </div>
        </div>

        <!-- Messages -->
        <div ref="messageContainer" class="messages-area">
          <div v-if="currentMessages.length === 0" class="welcome-chat">
            <div class="welcome-icon">
              <i class="bi bi-robot"></i>
            </div>

            <h3>Bạn muốn hỏi gì hôm nay?</h3>
            <p>
              Chọn môn học và nhập câu hỏi. Hệ thống sẽ tìm nội dung liên quan
              từ tài liệu bạn đã lưu.
            </p>

            <div class="suggestion-list">
              <button
                v-for="prompt in suggestedPrompts"
                :key="prompt"
                class="suggestion-btn"
                @click="sendSuggestedQuestion(prompt)"
              >
                <i class="bi bi-lightbulb"></i>
                {{ prompt }}
              </button>
            </div>
          </div>

          <div
            v-for="message in currentMessages"
            :key="message.id"
            class="message-row"
            :class="message.role === 'USER' ? 'user' : 'assistant'"
          >
            <div class="message-avatar">
              <i
                :class="
                  message.role === 'USER'
                    ? 'bi bi-person-fill'
                    : 'bi bi-robot'
                "
              ></i>
            </div>

            <div class="message-content">
              <div class="message-bubble">
                <p>{{ message.content }}</p>
              </div>

              <div class="message-meta">
                <span>{{ formatMessageTime(message.createdAt) }}</span>

                <span v-if="message.role === 'ASSISTANT'" class="model-badge">
                  {{ message.aiModel }}
                </span>
              </div>
            </div>
          </div>

          <div v-if="isLoading" class="message-row assistant">
            <div class="message-avatar">
              <i class="bi bi-robot"></i>
            </div>

            <div class="typing-bubble">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="chat-input-area">
          <div class="algorithm-note">
            <i class="bi bi-diagram-3"></i>
            Đang mô phỏng tìm kiếm bằng TF-IDF + Cosine Similarity trên tài liệu đã lưu.
          </div>

          <div class="input-row">
            <textarea
              v-model="question"
              rows="2"
              placeholder="Nhập câu hỏi của bạn, ví dụ: Giải thích vòng lặp for trong Python..."
              @keydown.enter.exact.prevent="sendQuestion"
            ></textarea>

            <button
              class="send-btn"
              :disabled="!question.trim() || isLoading"
              @click="sendQuestion"
            >
              <i class="bi bi-send-fill"></i>
            </button>
          </div>
        </div>
      </section>

      <!-- Retrieval Sources Panel -->
      <aside class="sources-panel">
        <div class="sources-header">
          <h5>Nguồn trả lời</h5>
          <span>Chat Sources</span>
        </div>

        <div v-if="currentSources.length === 0" class="sources-empty">
          <div class="source-empty-icon">
            <i class="bi bi-search"></i>
          </div>

          <p>
            Khi chatbot trả lời, các đoạn tài liệu liên quan sẽ xuất hiện tại đây.
          </p>
        </div>

        <div v-else class="source-list">
          <div
            v-for="source in currentSources"
            :key="source.id"
            class="source-card"
          >
            <div class="source-top">
              <div>
                <span class="rank-badge">#{{ source.rankOrder }}</span>
                <strong>{{ source.documentTitle }}</strong>
              </div>

              <span class="score-badge">
                {{ formatScore(source.similarityScore) }}%
              </span>
            </div>

            <p>{{ source.content }}</p>

            <div class="score-progress">
              <div
                class="score-progress-bar"
                :style="{ width: `${formatScore(source.similarityScore)}%` }"
              ></div>
            </div>

            <small>
              <i class="bi bi-book"></i>
              {{ getSubjectName(source.subjectId) }}
            </small>
          </div>
        </div>

        <!-- <div class="algorithm-card">
          <h5>Thuật toán sử dụng</h5>

          <div class="algorithm-item">
            <i class="bi bi-1-circle-fill"></i>
            <span>Tách câu hỏi thành từ khóa</span>
          </div>

          <div class="algorithm-item">
            <i class="bi bi-2-circle-fill"></i>
            <span>Biểu diễn nội dung bằng TF-IDF</span>
          </div>

          <div class="algorithm-item">
            <i class="bi bi-3-circle-fill"></i>
            <span>Tính Cosine Similarity</span>
          </div>

          <div class="algorithm-item">
            <i class="bi bi-4-circle-fill"></i>
            <span>Chọn đoạn phù hợp nhất</span>
          </div>
        </div> -->
      </aside>
    </div>

    <!-- Toast -->
    <div v-if="toastMessage" class="toast-message">
      <i class="bi bi-check-circle-fill"></i>
      {{ toastMessage }}
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'

const subjectStorageKey = 'studymate_subjects'
const documentStorageKey = 'studymate_documents'
const sessionStorageKey = 'studymate_chat_sessions'
const messageStorageKey = 'studymate_chat_messages'
const sourceStorageKey = 'studymate_chat_sources'

const defaultSubjects = [
  {
    id: 1,
    name: 'Perl & Python',
    color: '#6366F1',
  },
  {
    id: 2,
    name: 'System Integration',
    color: '#0891B2',
  },
  {
    id: 3,
    name: 'Cơ sở dữ liệu',
    color: '#16A34A',
  },
]

const defaultDocuments = [
  {
    id: 1,
    subjectId: '1',
    title: 'Vòng lặp trong Python',
    content:
      'Vòng lặp for trong Python dùng để duyệt qua các phần tử trong list, tuple hoặc chuỗi. Vòng lặp while tiếp tục thực hiện khi điều kiện còn đúng. Từ khóa break dùng để thoát khỏi vòng lặp.',
    chunks: [
      'Vòng lặp for trong Python dùng để duyệt qua các phần tử trong list, tuple hoặc chuỗi.',
      'Vòng lặp while tiếp tục thực hiện khi điều kiện còn đúng.',
      'Từ khóa break dùng để thoát khỏi vòng lặp.',
    ],
  },
  {
    id: 2,
    subjectId: '1',
    title: 'FastAPI cơ bản',
    content:
      'FastAPI là framework Python giúp xây dựng REST API. Trong dự án StudyMate, FastAPI nhận câu hỏi từ Vue 3, xử lý dữ liệu và gọi Gemini API để tạo câu trả lời.',
    chunks: [
      'FastAPI là framework Python giúp xây dựng REST API.',
      'Trong dự án StudyMate, FastAPI nhận câu hỏi từ Vue 3, xử lý dữ liệu và gọi Gemini API để tạo câu trả lời.',
    ],
  },
  {
    id: 3,
    subjectId: '2',
    title: 'Mô hình tích hợp hệ thống',
    content:
      'Data Integration cho phép các hệ thống chia sẻ dữ liệu. Functional Integration kết nối hệ thống thông qua API hoặc message broker.',
    chunks: [
      'Data Integration cho phép các hệ thống chia sẻ dữ liệu.',
      'Functional Integration kết nối hệ thống thông qua API hoặc message broker.',
    ],
  },
]

const loadData = (key, defaultData) => {
  const storedData = localStorage.getItem(key)

  if (storedData) {
    return JSON.parse(storedData)
  }

  localStorage.setItem(key, JSON.stringify(defaultData))
  return defaultData
}

const subjects = ref(loadData(subjectStorageKey, defaultSubjects))
const documents = ref(loadData(documentStorageKey, defaultDocuments))
const sessions = ref(loadData(sessionStorageKey, []))
const messages = ref(loadData(messageStorageKey, []))
const sources = ref(loadData(sourceStorageKey, []))

const selectedSubjectId = ref(
  subjects.value.length > 0 ? String(subjects.value[0].id) : '',
)

const currentSessionId = ref(null)
const question = ref('')
const isLoading = ref(false)
const toastMessage = ref('')
const messageContainer = ref(null)

const sortedSessions = computed(() => {
  return [...sessions.value].sort(
    (first, second) =>
      new Date(second.updatedAt).getTime() -
      new Date(first.updatedAt).getTime(),
  )
})

const currentSession = computed(() => {
  return sessions.value.find(
    (session) => Number(session.id) === Number(currentSessionId.value),
  )
})

const currentMessages = computed(() => {
  return messages.value
    .filter(
      (message) =>
        Number(message.sessionId) === Number(currentSessionId.value),
    )
    .sort(
      (first, second) =>
        new Date(first.createdAt).getTime() -
        new Date(second.createdAt).getTime(),
    )
})

const lastAssistantMessage = computed(() => {
  return [...currentMessages.value]
    .reverse()
    .find((message) => message.role === 'ASSISTANT')
})

const currentSources = computed(() => {
  if (!lastAssistantMessage.value) {
    return []
  }

  return sources.value
    .filter(
      (source) =>
        Number(source.assistantMessageId) ===
        Number(lastAssistantMessage.value.id),
    )
    .sort((first, second) => first.rankOrder - second.rankOrder)
})

const totalQuestions = computed(() => {
  return messages.value.filter((message) => message.role === 'USER').length
})

const suggestedPrompts = computed(() => {
  const subjectName = getSubjectName(selectedSubjectId.value)

  if (subjectName === 'Perl & Python') {
    return [
      'Giải thích vòng lặp for trong Python',
      'FastAPI dùng để làm gì trong dự án?',
      'Sự khác nhau giữa for và while là gì?',
    ]
  }

  if (subjectName === 'System Integration') {
    return [
      'Data Integration là gì?',
      'Functional Integration hoạt động như thế nào?',
      'API có vai trò gì trong tích hợp hệ thống?',
    ]
  }

  return [
    'Giải thích nội dung quan trọng của môn học',
    'Cho mình biết nội dung cần ưu tiên ôn',
    'Tài liệu này nói về vấn đề gì?',
  ]
})

const persistChatData = () => {
  localStorage.setItem(sessionStorageKey, JSON.stringify(sessions.value))
  localStorage.setItem(messageStorageKey, JSON.stringify(messages.value))
  localStorage.setItem(sourceStorageKey, JSON.stringify(sources.value))
}

const getSubjectName = (subjectId) => {
  const subject = subjects.value.find(
    (item) => String(item.id) === String(subjectId),
  )

  return subject ? subject.name : 'Không xác định'
}

const formatShortDate = (dateValue) => {
  return new Date(dateValue).toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
  })
}

const formatMessageTime = (dateValue) => {
  return new Date(dateValue).toLocaleString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    day: '2-digit',
    month: '2-digit',
  })
}

const formatScore = (score) => {
  return Math.round(Number(score) * 100)
}

const showToast = (message) => {
  toastMessage.value = message

  setTimeout(() => {
    toastMessage.value = ''
  }, 2400)
}

const scrollToBottom = async () => {
  await nextTick()

  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

const createNewChat = () => {
  const newSession = {
    id: Date.now(),
    subjectId: selectedSubjectId.value,
    title: 'Cuộc trò chuyện mới',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  }

  sessions.value.unshift(newSession)
  currentSessionId.value = newSession.id
  question.value = ''

  persistChatData()
}

const selectSession = (session) => {
  currentSessionId.value = session.id
  selectedSubjectId.value = String(session.subjectId)
  scrollToBottom()
}

const deleteSession = (sessionId) => {
  const messageIds = messages.value
    .filter((message) => Number(message.sessionId) === Number(sessionId))
    .map((message) => message.id)

  sessions.value = sessions.value.filter(
    (session) => Number(session.id) !== Number(sessionId),
  )

  messages.value = messages.value.filter(
    (message) => Number(message.sessionId) !== Number(sessionId),
  )

  sources.value = sources.value.filter(
    (source) => !messageIds.includes(source.assistantMessageId),
  )

  if (Number(currentSessionId.value) === Number(sessionId)) {
    if (sessions.value.length > 0) {
      selectSession(sessions.value[0])
    } else {
      createNewChat()
    }
  }

  persistChatData()
  showToast('Đã xóa cuộc trò chuyện.')
}

const handleSubjectChange = () => {
  if (!currentSession.value) {
    createNewChat()
    return
  }

  if (currentMessages.value.length > 0) {
    createNewChat()
    return
  }

  currentSession.value.subjectId = selectedSubjectId.value
  currentSession.value.updatedAt = new Date().toISOString()
  persistChatData()
}

const normalizeText = (text) => {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd')
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter((word) => word.length > 1)
}

const getDocumentChunks = (subjectId) => {
  const subjectDocuments = documents.value.filter(
    (document) => String(document.subjectId) === String(subjectId),
  )

  const chunks = []

  subjectDocuments.forEach((document) => {
    const documentChunks =
      document.chunks && document.chunks.length > 0
        ? document.chunks
        : [document.content]

    documentChunks.forEach((chunk, index) => {
      chunks.push({
        id: `${document.id}-${index + 1}`,
        documentId: document.id,
        documentTitle: document.title,
        subjectId: document.subjectId,
        content: chunk,
      })
    })
  })

  return chunks
}

const calculateSimilarityResults = (inputQuestion, subjectId) => {
  const chunks = getDocumentChunks(subjectId)

  if (chunks.length === 0) {
    return []
  }

  const questionTokens = normalizeText(inputQuestion)
  const tokenizedChunks = chunks.map((chunk) => normalizeText(chunk.content))
  const vocabulary = [...new Set(questionTokens)]

  const totalDocuments = tokenizedChunks.length

  const calculateVector = (tokens) => {
    return vocabulary.map((term) => {
      const termFrequency =
        tokens.filter((token) => token === term).length /
        Math.max(tokens.length, 1)

      const documentFrequency = tokenizedChunks.filter((chunkTokens) =>
        chunkTokens.includes(term),
      ).length

      const inverseDocumentFrequency =
        Math.log((totalDocuments + 1) / (documentFrequency + 1)) + 1

      return termFrequency * inverseDocumentFrequency
    })
  }

  const cosineSimilarity = (firstVector, secondVector) => {
    const dotProduct = firstVector.reduce(
      (total, value, index) => total + value * secondVector[index],
      0,
    )

    const firstMagnitude = Math.sqrt(
      firstVector.reduce((total, value) => total + value * value, 0),
    )

    const secondMagnitude = Math.sqrt(
      secondVector.reduce((total, value) => total + value * value, 0),
    )

    if (firstMagnitude === 0 || secondMagnitude === 0) {
      return 0
    }

    return dotProduct / (firstMagnitude * secondMagnitude)
  }

  const questionVector = calculateVector(questionTokens)

  return chunks
    .map((chunk, index) => {
      const chunkVector = calculateVector(tokenizedChunks[index])

      return {
        ...chunk,
        similarityScore: cosineSimilarity(questionVector, chunkVector),
      }
    })
    .filter((chunk) => chunk.similarityScore > 0)
    .sort(
      (first, second) =>
        second.similarityScore - first.similarityScore,
    )
    .slice(0, 3)
}

const generateDemoAnswer = (inputQuestion, retrievedSources) => {
  if (retrievedSources.length === 0) {
    return (
      'Mình chưa tìm thấy đoạn tài liệu phù hợp với câu hỏi này trong môn học đã chọn. ' +
      'Bạn hãy thêm tài liệu liên quan hoặc thử đặt câu hỏi bằng từ khóa cụ thể hơn.'
    )
  }

  const bestSource = retrievedSources[0]

  let answer =
    `Dựa trên tài liệu "${bestSource.documentTitle}", nội dung liên quan nhất là: ` +
    `${bestSource.content}`

  if (retrievedSources.length > 1) {
    answer +=
      ' Ngoài ra, hệ thống cũng tìm thấy thêm các đoạn nội dung liên quan ở phần nguồn tham khảo bên phải.'
  }

  answer +=
    ' Hiện tại đây là câu trả lời mô phỏng theo tài liệu; khi kết nối backend, Gemini sẽ diễn giải chi tiết và tự nhiên hơn.'

  return answer
}

const sendSuggestedQuestion = (prompt) => {
  question.value = prompt
  sendQuestion()
}

const sendQuestion = async () => {
  const inputQuestion = question.value.trim()

  if (!inputQuestion || isLoading.value) {
    return
  }

  if (!currentSession.value) {
    createNewChat()
  }

  const session = currentSession.value
  const userMessageId = Date.now()

  messages.value.push({
    id: userMessageId,
    sessionId: session.id,
    role: 'USER',
    content: inputQuestion,
    aiModel: null,
    createdAt: new Date().toISOString(),
  })

  const userQuestionsInSession = messages.value.filter(
    (message) =>
      Number(message.sessionId) === Number(session.id) &&
      message.role === 'USER',
  )

  if (userQuestionsInSession.length === 1) {
    session.title =
      inputQuestion.length > 34
        ? `${inputQuestion.slice(0, 34)}...`
        : inputQuestion
  }

  session.subjectId = selectedSubjectId.value
  session.updatedAt = new Date().toISOString()

  question.value = ''
  isLoading.value = true
  persistChatData()
  await scrollToBottom()

  const retrievedSources = calculateSimilarityResults(
    inputQuestion,
    selectedSubjectId.value,
  )

  setTimeout(async () => {
    const assistantMessageId = Date.now() + 1

    messages.value.push({
      id: assistantMessageId,
      sessionId: session.id,
      role: 'ASSISTANT',
      content: generateDemoAnswer(inputQuestion, retrievedSources),
      aiModel: 'Demo Retrieval',
      createdAt: new Date().toISOString(),
    })

    sources.value = sources.value.filter(
      (source) =>
        Number(source.assistantMessageId) !== Number(assistantMessageId),
    )

    retrievedSources.forEach((source, index) => {
      sources.value.push({
        id: `${assistantMessageId}-${index + 1}`,
        assistantMessageId,
        documentId: source.documentId,
        documentTitle: source.documentTitle,
        subjectId: source.subjectId,
        content: source.content,
        similarityScore: source.similarityScore,
        rankOrder: index + 1,
      })
    })

    session.updatedAt = new Date().toISOString()
    isLoading.value = false
    persistChatData()

    await scrollToBottom()
  }, 750)
}

onMounted(() => {
  if (sessions.value.length === 0) {
    createNewChat()
  } else {
    selectSession(sortedSessions.value[0])
  }
})
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
  height: 104px;
  padding: 20px;
  border-radius: 18px;
  border: 1px solid #edf0f5;
  background: white;
  display: flex;
  align-items: center;
  gap: 16px;
}

.summary-icon {
  width: 53px;
  height: 53px;
  border-radius: 14px;
  font-size: 24px;
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

.summary-icon.green {
  color: #16a34a;
  background: #f0fdf4;
}

.summary-icon.orange {
  color: #f97316;
  background: #fff7ed;
}

.summary-card p {
  margin: 0 0 5px;
  color: #6b7280;
  font-size: 14px;
}

.summary-card h3 {
  margin: 0;
  font-size: 27px;
  font-weight: 700;
}

.chat-layout {
  height: calc(100vh - 330px);
  min-height: 620px;
  display: grid;
  grid-template-columns: 260px minmax(420px, 1fr) 300px;
  gap: 18px;
}

.history-panel,
.chat-panel,
.sources-panel {
  border: 1px solid #edf0f5;
  border-radius: 19px;
  background: white;
  overflow: hidden;
}

.history-panel {
  padding: 17px 12px;
}

.history-header {
  padding: 0 7px 14px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-header h5 {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}

.small-add-btn {
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 9px;
  color: #6366f1;
  background: #eef2ff;
}

.history-list {
  padding-top: 13px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.history-item {
  width: 100%;
  padding: 11px 8px;
  border: none;
  border-radius: 12px;
  background: transparent;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 9px;
}

.history-item:hover,
.history-item.active {
  background: #eef2ff;
}

.history-icon {
  width: 33px;
  height: 33px;
  flex-shrink: 0;
  border-radius: 9px;
  color: #6366f1;
  background: #f5f3ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.history-content {
  min-width: 0;
  flex: 1;
}

.history-content p {
  margin: 0 0 4px;
  color: #111827;
  font-size: 13px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-content small {
  color: #6b7280;
  font-size: 11px;
}

.delete-session {
  display: none;
  color: #dc2626;
}

.history-item:hover .delete-session {
  display: block;
}

.chat-panel {
  display: flex;
  flex-direction: column;
}

.chat-header {
  height: 76px;
  padding: 13px 19px;
  border-bottom: 1px solid #edf0f5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.chat-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bot-avatar {
  width: 47px;
  height: 47px;
  border-radius: 14px;
  color: white;
  background: #6366f1;
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-title h5 {
  margin: 0 0 4px;
  font-weight: 700;
}

.chat-title p {
  margin: 0;
  color: #6b7280;
  font-size: 12px;
}

.online-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  margin-right: 4px;
  border-radius: 50%;
  background: #16a34a;
}

.subject-select label {
  display: block;
  margin-bottom: 4px;
  color: #6b7280;
  font-size: 11px;
  font-weight: 600;
}

.subject-select select {
  min-width: 170px;
  height: 39px;
  padding: 0 10px;
  border: 1px solid #e5e7eb;
  border-radius: 9px;
  color: #374151;
  background: white;
}

.messages-area {
  flex: 1;
  padding: 22px;
  background: #f9fafc;
  overflow-y: auto;
}

.welcome-chat {
  max-width: 570px;
  margin: 48px auto 0;
  text-align: center;
}

.welcome-icon {
  width: 67px;
  height: 67px;
  margin: 0 auto 17px;
  border-radius: 20px;
  color: #6366f1;
  background: #eef2ff;
  font-size: 33px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-chat h3 {
  margin: 0 0 9px;
  font-size: 22px;
  font-weight: 700;
}

.welcome-chat p {
  margin: 0 auto 24px;
  max-width: 470px;
  color: #6b7280;
  line-height: 1.6;
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.suggestion-btn {
  padding: 13px 15px;
  border: 1px solid #e0e7ff;
  border-radius: 12px;
  color: #374151;
  background: white;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 9px;
}

.suggestion-btn i {
  color: #6366f1;
}

.suggestion-btn:hover {
  border-color: #6366f1;
  background: #f8faff;
}

.message-row {
  margin-bottom: 19px;
  display: flex;
  gap: 11px;
}

.message-row.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 39px;
  height: 39px;
  flex-shrink: 0;
  border-radius: 12px;
  color: white;
  background: #6366f1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-row.user .message-avatar {
  background: #111827;
}

.message-content {
  max-width: 75%;
}

.message-bubble {
  padding: 13px 16px;
  border-radius: 15px;
  color: #111827;
  background: white;
  border: 1px solid #edf0f5;
}

.message-row.user .message-bubble {
  color: white;
  background: #6366f1;
  border-color: #6366f1;
}

.message-bubble p {
  margin: 0;
  line-height: 1.65;
  white-space: pre-wrap;
}

.message-meta {
  margin-top: 6px;
  color: #9ca3af;
  font-size: 11px;
  display: flex;
  gap: 7px;
  align-items: center;
}

.message-row.user .message-meta {
  justify-content: flex-end;
}

.model-badge {
  padding: 3px 8px;
  border-radius: 14px;
  color: #4338ca;
  background: #eef2ff;
  font-weight: 600;
}

.typing-bubble {
  height: 44px;
  padding: 0 16px;
  border-radius: 15px;
  border: 1px solid #edf0f5;
  background: white;
  display: flex;
  align-items: center;
  gap: 5px;
}

.typing-bubble span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #9ca3af;
  animation: typing 1s infinite;
}

.typing-bubble span:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-bubble span:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes typing {
  0%, 100% {
    opacity: 0.4;
    transform: translateY(0);
  }

  50% {
    opacity: 1;
    transform: translateY(-3px);
  }
}

.chat-input-area {
  padding: 15px 18px 17px;
  border-top: 1px solid #edf0f5;
  background: white;
}

.algorithm-note {
  margin-bottom: 10px;
  color: #6366f1;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 11px;
}

.input-row textarea {
  flex: 1;
  min-height: 53px;
  max-height: 120px;
  padding: 14px;
  border: 1px solid #e5e7eb;
  border-radius: 13px;
  outline: none;
  resize: none;
}

.input-row textarea:focus {
  border-color: #6366f1;
}

.send-btn {
  width: 53px;
  height: 53px;
  border: none;
  border-radius: 13px;
  color: white;
  background: #6366f1;
  font-size: 19px;
}

.send-btn:disabled {
  cursor: not-allowed;
  background: #c7d2fe;
}

.sources-panel {
  padding: 19px;
}

.sources-header {
  margin-bottom: 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sources-header h5 {
  margin: 0;
  font-weight: 700;
}

.sources-header span {
  padding: 5px 9px;
  border-radius: 20px;
  color: #4338ca;
  background: #eef2ff;
  font-size: 11px;
  font-weight: 700;
}

.sources-empty {
  padding: 40px 10px;
  text-align: center;
}

.source-empty-icon {
  width: 55px;
  height: 55px;
  margin: 0 auto 13px;
  border-radius: 50%;
  color: #6366f1;
  background: #eef2ff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.sources-empty p {
  color: #6b7280;
  font-size: 13px;
  line-height: 1.6;
}

.source-list {
  max-height: 376px;
  overflow-y: auto;
}

.source-card {
  margin-bottom: 11px;
  padding: 13px;
  border: 1px solid #e0e7ff;
  border-radius: 12px;
  background: #fafaff;
}

.source-top {
  margin-bottom: 9px;
  display: flex;
  justify-content: space-between;
  gap: 7px;
}

.source-top div {
  min-width: 0;
}

.source-top strong {
  display: block;
  margin-top: 6px;
  color: #111827;
  font-size: 13px;
}

.rank-badge {
  padding: 3px 7px;
  border-radius: 12px;
  color: #4338ca;
  background: #eef2ff;
  font-size: 11px;
  font-weight: 700;
}

.score-badge {
  color: #16a34a;
  font-size: 13px;
  font-weight: 700;
}

.source-card p {
  margin: 0 0 10px;
  color: #4b5563;
  font-size: 12px;
  line-height: 1.55;
}

.score-progress {
  height: 6px;
  margin-bottom: 9px;
  border-radius: 20px;
  background: #e5e7eb;
  overflow: hidden;
}

.score-progress-bar {
  height: 100%;
  border-radius: 20px;
  background: #16a34a;
}

.source-card small {
  color: #6b7280;
  font-size: 11px;
}

.algorithm-card {
  margin-top: 18px;
  padding: 15px;
  border-radius: 13px;
  background: #111827;
  color: white;
}

.algorithm-card h5 {
  margin: 0 0 14px;
  font-size: 14px;
  font-weight: 700;
}

.algorithm-item {
  margin-bottom: 11px;
  color: #cbd5e1;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 9px;
}

.algorithm-item:last-child {
  margin-bottom: 0;
}

.algorithm-item i {
  color: #818cf8;
  font-size: 16px;
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

@media (max-width: 1350px) {
  .chat-layout {
    grid-template-columns: 235px minmax(380px, 1fr);
  }

  .sources-panel {
    grid-column: 1 / -1;
  }
}

@media (max-width: 850px) {
  .page-header,
  .chat-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .chat-layout {
    height: auto;
    display: flex;
    flex-direction: column;
  }

  .history-panel,
  .chat-panel,
  .sources-panel {
    min-height: auto;
  }

  .messages-area {
    min-height: 500px;
  }
}
</style>