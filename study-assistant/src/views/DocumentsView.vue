<template>
  <div class="documents-page">
    <!-- Header -->
    <div class="page-header">
      <div>
        <h2>Tài liệu học tập</h2>
        <p>Lưu tài liệu theo từng môn học để chatbot hỗ trợ trả lời chính xác hơn.</p>
      </div>

      <button class="primary-btn" @click="openAddModal">
        <i class="bi bi-plus-lg"></i>
        Thêm tài liệu
      </button>
    </div>

    <!-- Summary -->
    <div class="row g-4 mb-4">
      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon purple">
            <i class="bi bi-file-earmark-text-fill"></i>
          </div>

          <div>
            <p>Tổng tài liệu</p>
            <h3>{{ documents.length }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon blue">
            <i class="bi bi-book-half"></i>
          </div>

          <div>
            <p>Môn có tài liệu</p>
            <h3>{{ subjectsWithDocuments }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon green">
            <i class="bi bi-diagram-3-fill"></i>
          </div>

          <div>
            <p>Đoạn đã xử lý</p>
            <h3>{{ totalChunks }}</h3>
          </div>
        </div>
      </div>

      <div class="col-xl-3 col-md-6">
        <div class="summary-card">
          <div class="summary-icon orange">
            <i class="bi bi-robot"></i>
          </div>

          <div>
            <p>Sẵn sàng cho AI</p>
            <h3>{{ processedDocuments }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Layout -->
    <div class="row g-4">
      <!-- Documents List -->
      <div class="col-xl-8">
        <div class="content-card">
          <div class="toolbar">
            <div>
              <h5>Kho tài liệu của bạn</h5>
              <p>Tìm kiếm nội dung được dùng làm dữ liệu đầu vào cho chatbot.</p>
            </div>

            <div class="filters">
              <div class="search-box">
                <i class="bi bi-search"></i>
                <input
                  v-model="searchKeyword"
                  type="text"
                  placeholder="Tìm tài liệu..."
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
            </div>
          </div>

          <!-- Empty -->
          <div v-if="filteredDocuments.length === 0" class="empty-state">
            <div class="empty-icon">
              <i class="bi bi-file-earmark-x"></i>
            </div>

            <h5>Chưa có tài liệu phù hợp</h5>
            <p>Hãy thêm tài liệu học tập để chatbot có thể hỗ trợ bạn.</p>

            <button class="primary-btn" @click="openAddModal">
              <i class="bi bi-plus-lg"></i>
              Thêm tài liệu
            </button>
          </div>

          <!-- Document Cards -->
          <div v-else class="document-list">
            <div
              v-for="document in filteredDocuments"
              :key="document.id"
              class="document-card"
            >
              <div class="document-icon">
                <i
                  :class="
                    document.sourceType === 'FILE'
                      ? 'bi bi-file-earmark-arrow-up-fill'
                      : 'bi bi-file-earmark-text-fill'
                  "
                ></i>
              </div>

              <div class="document-main">
                <div class="document-heading">
                  <div>
                    <div class="title-row">
                      <h4>{{ document.title }}</h4>

                      <span
                        class="status-badge"
                        :class="document.processingStatus.toLowerCase()"
                      >
                        {{ getProcessingText(document.processingStatus) }}
                      </span>
                    </div>

                    <p class="document-subject">
                      <i class="bi bi-book"></i>
                      {{ getSubjectName(document.subjectId) }}

                      <span class="separator">•</span>

                      <i class="bi bi-calendar3"></i>
                      {{ formatDate(document.createdAt) }}
                    </p>
                  </div>

                  <div class="action-group">
                    <button
                      class="action-btn view"
                      title="Xem chi tiết"
                      @click="openDetailModal(document)"
                    >
                      <i class="bi bi-eye"></i>
                    </button>

                    <button
                      class="action-btn edit"
                      title="Sửa tài liệu"
                      @click="openEditModal(document)"
                    >
                      <i class="bi bi-pencil-square"></i>
                    </button>

                    <button
                      class="action-btn delete"
                      title="Xóa tài liệu"
                      @click="confirmDelete(document)"
                    >
                      <i class="bi bi-trash3"></i>
                    </button>
                  </div>
                </div>

                <p class="content-preview">
                  {{ getContentPreview(document.content) }}
                </p>

                <div class="document-footer">
                  <span class="meta-badge">
                    <i class="bi bi-layers-fill"></i>
                    {{ document.chunks.length }} đoạn nội dung
                  </span>

                  <span class="meta-badge">
                    <i class="bi bi-fonts"></i>
                    {{ countWords(document.content) }} từ
                  </span>

                  <span
                    v-if="document.fileName"
                    class="meta-badge file"
                  >
                    <i class="bi bi-paperclip"></i>
                    {{ document.fileName }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Algorithm Side Panel -->
      <div class="col-xl-4">
        <!-- <div class="ai-info-card mb-4">
          <div class="ai-icon">
            <i class="bi bi-stars"></i>
          </div>

          <h5>Dữ liệu cho chatbot</h5>
          <p>
            Tài liệu sau khi thêm sẽ được chia thành các đoạn ngắn. Khi bạn đặt
            câu hỏi, hệ thống tìm đoạn có nội dung liên quan nhất để gửi cho AI.
          </p>

          <div class="flow-step">
            <span>1</span>
            <div>
              <strong>Thêm tài liệu</strong>
              <small>Lưu nội dung theo môn học</small>
            </div>
          </div>

          <div class="flow-line"></div>

          <div class="flow-step">
            <span>2</span>
            <div>
              <strong>Tách đoạn nội dung</strong>
              <small>Lưu vào document_chunks</small>
            </div>
          </div>

          <div class="flow-line"></div>

          <div class="flow-step">
            <span>3</span>
            <div>
              <strong>Tìm kiếm thông minh</strong>
              <small>TF-IDF + Cosine Similarity</small>
            </div>
          </div>

          <div class="flow-line"></div>

          <div class="flow-step">
            <span>4</span>
            <div>
              <strong>Chatbot trả lời</strong>
              <small>Gemini dựa trên đoạn tìm được</small>
            </div>
          </div>
        </div> -->

        <div class="subject-doc-card">
          <h5>Tài liệu theo môn học</h5>

          <div
            v-for="subject in subjects"
            :key="subject.id"
            class="subject-document-item"
          >
            <div class="subject-color" :style="{ backgroundColor: subject.color || '#6366F1' }"></div>

            <div>
              <p>{{ subject.name }}</p>
              <small>{{ getDocumentCountBySubject(subject.id) }} tài liệu</small>
            </div>

            <strong>{{ getDocumentCountBySubject(subject.id) }}</strong>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
      <div class="modal-card">
        <div class="modal-header-custom">
          <div>
            <h4>
              {{ isEditing ? 'Cập nhật tài liệu' : 'Thêm tài liệu học tập' }}
            </h4>
            <p>Lưu nội dung để sử dụng cho chatbot hỏi đáp.</p>
          </div>

          <button class="close-btn" @click="closeModal">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <form @submit.prevent="saveDocument">
          <div class="form-group">
            <label>Tiêu đề tài liệu <span>*</span></label>
            <input
              v-model.trim="form.title"
              type="text"
              placeholder="Ví dụ: Vòng lặp trong Python"
              :class="{ invalid: errors.title }"
            />
            <small v-if="errors.title" class="error-text">
              {{ errors.title }}
            </small>
          </div>

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

          <div class="source-type-box">
            <label class="source-option" :class="{ active: form.sourceType === 'TEXT' }">
              <input v-model="form.sourceType" type="radio" value="TEXT" />
              <i class="bi bi-pencil-square"></i>
              <div>
                <strong>Nhập văn bản</strong>
                <small>Gõ hoặc dán nội dung bài học</small>
              </div>
            </label>

            <label class="source-option" :class="{ active: form.sourceType === 'FILE' }">
              <input v-model="form.sourceType" type="radio" value="FILE" />
              <i class="bi bi-file-earmark-arrow-up"></i>
              <div>
                <strong>Tải file TXT</strong>
                <small>Đọc nội dung file văn bản</small>
              </div>
            </label>
          </div>

          <div v-if="form.sourceType === 'FILE'" class="upload-area">
            <input
              ref="fileInput"
              type="file"
              accept=".txt"
              @change="handleFileUpload"
            />

            <div class="upload-content">
              <i class="bi bi-cloud-arrow-up-fill"></i>
              <p>
                {{ form.fileName || 'Chọn file văn bản .txt để đọc nội dung' }}
              </p>
              <small>PDF và DOCX sẽ xử lý bằng Python backend sau.</small>
            </div>
          </div>

          <div class="form-group">
            <label>Nội dung tài liệu <span>*</span></label>
            <textarea
              v-model.trim="form.content"
              rows="9"
              placeholder="Nhập hoặc dán nội dung tài liệu tại đây..."
              :class="{ invalid: errors.content }"
            ></textarea>
            <div class="content-counter">
              <small v-if="errors.content" class="error-text">
                {{ errors.content }}
              </small>
              <small v-else>
                {{ countWords(form.content) }} từ ·
                {{ previewChunks.length }} đoạn dự kiến
              </small>
            </div>
          </div>

          <!-- Chunk preview -->
          <div v-if="previewChunks.length > 0" class="chunk-preview-box">
            <div class="chunk-preview-header">
              <h5>Xem trước đoạn nội dung</h5>
              <span>{{ previewChunks.length }} đoạn</span>
            </div>

            <div
              v-for="(chunk, index) in previewChunks.slice(0, 3)"
              :key="index"
              class="chunk-preview-item"
            >
              <strong>Đoạn {{ index + 1 }}</strong>
              <p>{{ chunk }}</p>
            </div>

            <small v-if="previewChunks.length > 3" class="more-chunks">
              Và {{ previewChunks.length - 3 }} đoạn khác...
            </small>
          </div>

          <div class="modal-footer-custom">
            <button type="button" class="cancel-btn" @click="closeModal">
              Hủy
            </button>

            <button type="submit" class="save-btn">
              <i class="bi bi-check-lg"></i>
              {{ isEditing ? 'Lưu thay đổi' : 'Lưu tài liệu' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Detail Modal -->
    <div
      v-if="selectedDocument"
      class="modal-overlay"
      @click.self="selectedDocument = null"
    >
      <div class="detail-modal">
        <div class="modal-header-custom">
          <div>
            <h4>{{ selectedDocument.title }}</h4>
            <p>
              {{ getSubjectName(selectedDocument.subjectId) }} ·
              {{ selectedDocument.chunks.length }} đoạn nội dung
            </p>
          </div>

          <button class="close-btn" @click="selectedDocument = null">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <div class="full-content">
          <h5>Nội dung tài liệu</h5>
          <p>{{ selectedDocument.content }}</p>
        </div>

        <div class="chunks-detail">
          <div class="detail-title">
            <h5>Các đoạn dùng cho chatbot</h5>
            <span>document_chunks</span>
          </div>

          <div
            v-for="(chunk, index) in selectedDocument.chunks"
            :key="index"
            class="chunk-detail-item"
          >
            <div class="chunk-number">{{ index + 1 }}</div>
            <p>{{ chunk }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Modal -->
    <div v-if="documentToDelete" class="modal-overlay" @click.self="documentToDelete = null">
      <div class="delete-modal">
        <div class="delete-icon">
          <i class="bi bi-trash3"></i>
        </div>

        <h4>Xóa tài liệu?</h4>
        <p>
          Bạn có chắc muốn xóa tài liệu
          <strong>{{ documentToDelete.title }}</strong> không?
        </p>

        <div class="delete-actions">
          <button class="cancel-btn" @click="documentToDelete = null">
            Hủy
          </button>

          <button class="confirm-delete-btn" @click="deleteDocument">
            Xóa tài liệu
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

const documentStorageKey = 'studymate_documents'
const subjectStorageKey = 'studymate_subjects'

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
  {
    id: 4,
    name: 'Lập trình Web',
    color: '#F97316',
  },
]

const loadSubjects = () => {
  const data = localStorage.getItem(subjectStorageKey)
  return data ? JSON.parse(data) : defaultSubjects
}

const subjects = ref(loadSubjects())

const getSubjectIdByName = (name, fallbackId) => {
  const subject = subjects.value.find((item) => item.name === name)
  return subject ? String(subject.id) : String(fallbackId)
}

const buildChunks = (content) => {
  if (!content || !content.trim()) {
    return []
  }

  const cleanContent = content.replace(/\s+/g, ' ').trim()

  const sentences = cleanContent
    .split(/(?<=[.!?])\s+/)
    .filter((sentence) => sentence.trim())

  const chunks = []
  let currentChunk = ''

  sentences.forEach((sentence) => {
    const candidate = currentChunk
      ? `${currentChunk} ${sentence}`
      : sentence

    if (candidate.length > 180 && currentChunk) {
      chunks.push(currentChunk.trim())
      currentChunk = sentence
    } else {
      currentChunk = candidate
    }
  })

  if (currentChunk) {
    chunks.push(currentChunk.trim())
  }

  return chunks.length > 0 ? chunks : [cleanContent]
}

const createDocument = ({
  id,
  subjectId,
  title,
  content,
  sourceType = 'TEXT',
  fileName = '',
  createdAt = new Date().toISOString(),
}) => ({
  id,
  subjectId,
  title,
  sourceType,
  fileName,
  content,
  processingStatus: 'DA_XU_LY',
  createdAt,
  chunks: buildChunks(content),
})

const defaultDocuments = [
  createDocument({
    id: 1,
    subjectId: getSubjectIdByName('Perl & Python', 1),
    title: 'Vòng lặp trong Python',
    content:
      'Vòng lặp for trong Python dùng để duyệt qua các phần tử trong list, tuple hoặc chuỗi. Vòng lặp while tiếp tục thực hiện khi điều kiện còn đúng. Từ khóa break dùng để thoát khỏi vòng lặp. Từ khóa continue dùng để bỏ qua lần lặp hiện tại.',
  }),
  createDocument({
    id: 2,
    subjectId: getSubjectIdByName('Perl & Python', 1),
    title: 'Hàm và FastAPI cơ bản',
    content:
      'Hàm trong Python được khai báo bằng từ khóa def và có thể nhận tham số đầu vào. FastAPI là framework Python giúp xây dựng REST API nhanh chóng. Trong dự án StudyMate, FastAPI nhận câu hỏi từ Vue 3 và gọi Gemini API để trả lời.',
  }),
  createDocument({
    id: 3,
    subjectId: getSubjectIdByName('System Integration', 2),
    title: 'Các mô hình tích hợp hệ thống',
    content:
      'Data Integration cho phép các hệ thống chia sẻ và đồng bộ dữ liệu. Functional Integration kết nối các hệ thống thông qua API hoặc message broker. Messaging hỗ trợ giao tiếp bất đồng bộ giữa các thành phần hệ thống.',
  }),
]

const loadDocuments = () => {
  const data = localStorage.getItem(documentStorageKey)

  if (data) {
    return JSON.parse(data)
  }

  localStorage.setItem(documentStorageKey, JSON.stringify(defaultDocuments))
  return defaultDocuments
}

const documents = ref(loadDocuments())

const searchKeyword = ref('')
const selectedSubject = ref('')
const isModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const selectedDocument = ref(null)
const documentToDelete = ref(null)
const toastMessage = ref('')
const fileInput = ref(null)

const emptyForm = () => ({
  subjectId: '',
  title: '',
  sourceType: 'TEXT',
  fileName: '',
  content: '',
})

const form = ref(emptyForm())

const errors = ref({
  title: '',
  subjectId: '',
  content: '',
})

const previewChunks = computed(() => {
  return buildChunks(form.value.content)
})

const totalChunks = computed(() => {
  return documents.value.reduce(
    (total, document) => total + document.chunks.length,
    0,
  )
})

const processedDocuments = computed(() => {
  return documents.value.filter(
    (document) => document.processingStatus === 'DA_XU_LY',
  ).length
})

const subjectsWithDocuments = computed(() => {
  return new Set(documents.value.map((document) => String(document.subjectId))).size
})

const filteredDocuments = computed(() => {
  const keyword = searchKeyword.value.toLowerCase()

  return [...documents.value]
    .filter((document) => {
      const matchesKeyword =
        document.title.toLowerCase().includes(keyword) ||
        document.content.toLowerCase().includes(keyword) ||
        getSubjectName(document.subjectId).toLowerCase().includes(keyword)

      const matchesSubject =
        !selectedSubject.value ||
        String(document.subjectId) === String(selectedSubject.value)

      return matchesKeyword && matchesSubject
    })
    .sort(
      (first, second) =>
        new Date(second.createdAt).getTime() - new Date(first.createdAt).getTime(),
    )
})

const persistDocuments = () => {
  localStorage.setItem(documentStorageKey, JSON.stringify(documents.value))
}

const getSubjectName = (subjectId) => {
  const subject = subjects.value.find(
    (item) => String(item.id) === String(subjectId),
  )

  return subject ? subject.name : 'Không xác định'
}

const getDocumentCountBySubject = (subjectId) => {
  return documents.value.filter(
    (document) => String(document.subjectId) === String(subjectId),
  ).length
}

const countWords = (content) => {
  if (!content || !content.trim()) {
    return 0
  }

  return content.trim().split(/\s+/).length
}

const getContentPreview = (content) => {
  if (content.length <= 180) {
    return content
  }

  return `${content.slice(0, 180)}...`
}

const formatDate = (dateValue) => {
  return new Date(dateValue).toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  })
}

const getProcessingText = (status) => {
  const statusText = {
    CHO_XU_LY: 'Chờ xử lý',
    DA_XU_LY: 'Đã xử lý',
    LOI: 'Lỗi',
  }

  return statusText[status] || status
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
    content: '',
  }
}

const openAddModal = () => {
  isEditing.value = false
  editingId.value = null
  form.value = emptyForm()
  resetErrors()
  isModalOpen.value = true
}

const openEditModal = (document) => {
  isEditing.value = true
  editingId.value = document.id
  form.value = {
    subjectId: String(document.subjectId),
    title: document.title,
    sourceType: document.sourceType,
    fileName: document.fileName || '',
    content: document.content,
  }

  resetErrors()
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  resetErrors()

  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const openDetailModal = (document) => {
  selectedDocument.value = document
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]

  if (!file) {
    return
  }

  if (!file.name.toLowerCase().endsWith('.txt')) {
    showToast('Hiện tại chỉ hỗ trợ đọc thử file .txt.')
    event.target.value = ''
    return
  }

  const reader = new FileReader()

  reader.onload = (readerEvent) => {
    form.value.fileName = file.name
    form.value.content = readerEvent.target.result

    if (!form.value.title) {
      form.value.title = file.name.replace(/\.txt$/i, '')
    }
  }

  reader.readAsText(file, 'UTF-8')
}

const validateForm = () => {
  resetErrors()
  let valid = true

  if (!form.value.title) {
    errors.value.title = 'Vui lòng nhập tiêu đề tài liệu.'
    valid = false
  }

  if (!form.value.subjectId) {
    errors.value.subjectId = 'Vui lòng chọn môn học.'
    valid = false
  }

  if (!form.value.content) {
    errors.value.content = 'Vui lòng nhập nội dung tài liệu.'
    valid = false
  }

  return valid
}

const saveDocument = () => {
  if (!validateForm()) {
    return
  }

  const documentData = createDocument({
    id: isEditing.value ? editingId.value : Date.now(),
    subjectId: form.value.subjectId,
    title: form.value.title,
    content: form.value.content,
    sourceType: form.value.sourceType,
    fileName: form.value.fileName,
    createdAt: isEditing.value
      ? documents.value.find((document) => document.id === editingId.value).createdAt
      : new Date().toISOString(),
  })

  if (isEditing.value) {
    const index = documents.value.findIndex(
      (document) => document.id === editingId.value,
    )

    documents.value[index] = documentData
    showToast('Cập nhật tài liệu thành công.')
  } else {
    documents.value.unshift(documentData)
    showToast('Thêm tài liệu thành công.')
  }

  persistDocuments()
  closeModal()
}

const confirmDelete = (document) => {
  documentToDelete.value = document
}

const deleteDocument = () => {
  documents.value = documents.value.filter(
    (document) => document.id !== documentToDelete.value.id,
  )

  persistDocuments()
  documentToDelete.value = null
  showToast('Đã xóa tài liệu.')
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

.summary-icon.green {
  color: #16a34a;
  background: #f0fdf4;
}

.summary-icon.orange {
  color: #f97316;
  background: #fff7ed;
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
.subject-doc-card {
  padding: 24px;
  border-radius: 19px;
  border: 1px solid #edf0f5;
  background: white;
}

.toolbar {
  margin-bottom: 24px;
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
  width: 225px;
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
  min-width: 160px;
  padding: 0 11px;
  border: 1px solid #e5e7eb;
  border-radius: 11px;
  color: #374151;
  background: white;
}

.document-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.document-card {
  padding: 19px;
  border: 1px solid #edf0f5;
  border-radius: 16px;
  display: flex;
  gap: 17px;
  transition: 0.2s;
}

.document-card:hover {
  border-color: #c7d2fe;
  box-shadow: 0 5px 17px rgba(15, 23, 42, 0.05);
}

.document-icon {
  width: 55px;
  height: 55px;
  flex-shrink: 0;
  border-radius: 14px;
  color: #6366f1;
  background: #eef2ff;
  font-size: 25px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.document-main {
  flex: 1;
}

.document-heading {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 9px;
  flex-wrap: wrap;
}

.title-row h4 {
  margin: 0;
  color: #111827;
  font-size: 17px;
  font-weight: 700;
}

.status-badge {
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
}

.status-badge.da_xu_ly {
  color: #15803d;
  background: #f0fdf4;
}

.status-badge.cho_xu_ly {
  color: #ea580c;
  background: #fff7ed;
}

.status-badge.loi {
  color: #dc2626;
  background: #fef2f2;
}

.document-subject {
  margin: 8px 0 0;
  color: #6b7280;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 7px;
}

.separator {
  margin: 0 3px;
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

.action-btn.view {
  color: #2563eb;
  background: #eff6ff;
}

.action-btn.edit {
  color: #ea580c;
  background: #fff7ed;
}

.action-btn.delete {
  color: #dc2626;
  background: #fef2f2;
}

.content-preview {
  margin: 14px 0;
  color: #4b5563;
  font-size: 14px;
  line-height: 1.6;
}

.document-footer {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-badge {
  padding: 6px 11px;
  border-radius: 20px;
  color: #4338ca;
  background: #eef2ff;
  font-size: 12px;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.meta-badge.file {
  color: #0369a1;
  background: #f0f9ff;
}

.ai-info-card {
  padding: 24px;
  border-radius: 19px;
  color: white;
  background: #111827;
}

.ai-icon {
  width: 52px;
  height: 52px;
  margin-bottom: 17px;
  border-radius: 14px;
  color: white;
  background: #6366f1;
  font-size: 25px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-info-card h5 {
  margin: 0 0 9px;
  font-weight: 700;
}

.ai-info-card > p {
  margin: 0 0 23px;
  color: #cbd5e1;
  font-size: 14px;
  line-height: 1.6;
}

.flow-step {
  display: flex;
  align-items: center;
  gap: 12px;
}

.flow-step > span {
  width: 30px;
  height: 30px;
  flex-shrink: 0;
  border-radius: 50%;
  color: white;
  background: #6366f1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.flow-step strong {
  display: block;
  font-size: 14px;
}

.flow-step small {
  color: #94a3b8;
  font-size: 12px;
}

.flow-line {
  width: 2px;
  height: 20px;
  margin: 6px 0 6px 14px;
  background: #374151;
}

.subject-doc-card h5 {
  margin: 0 0 18px;
  font-weight: 700;
}

.subject-document-item {
  padding: 12px 0;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  gap: 11px;
}

.subject-document-item:last-child {
  border-bottom: none;
}

.subject-color {
  width: 8px;
  height: 39px;
  border-radius: 20px;
}

.subject-document-item div:nth-child(2) {
  flex: 1;
}

.subject-document-item p {
  margin: 0 0 3px;
  color: #111827;
  font-size: 14px;
  font-weight: 600;
}

.subject-document-item small {
  color: #6b7280;
}

.subject-document-item strong {
  color: #4338ca;
  font-size: 18px;
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

.modal-card,
.detail-modal {
  width: 720px;
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

.form-group textarea {
  resize: vertical;
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
  color: #dc2626;
  font-size: 12px;
}

.source-type-box {
  margin-bottom: 18px;
  display: flex;
  gap: 13px;
}

.source-option {
  flex: 1;
  padding: 15px;
  border: 1px solid #e5e7eb;
  border-radius: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
}

.source-option.active {
  border-color: #6366f1;
  background: #f8faff;
}

.source-option input {
  display: none;
}

.source-option i {
  color: #6366f1;
  font-size: 24px;
}

.source-option strong {
  display: block;
  color: #111827;
  font-size: 14px;
}

.source-option small {
  color: #6b7280;
  font-size: 12px;
}

.upload-area {
  position: relative;
  margin-bottom: 18px;
  padding: 22px;
  border: 2px dashed #c7d2fe;
  border-radius: 14px;
  background: #f8faff;
  text-align: center;
}

.upload-area input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.upload-content i {
  color: #6366f1;
  font-size: 33px;
}

.upload-content p {
  margin: 8px 0 4px;
  font-weight: 600;
}

.upload-content small {
  color: #6b7280;
}

.content-counter {
  margin-top: 7px;
  color: #6b7280;
  font-size: 12px;
}

.chunk-preview-box {
  margin-bottom: 23px;
  padding: 16px;
  border-radius: 13px;
  border: 1px solid #e0e7ff;
  background: #f8faff;
}

.chunk-preview-header,
.detail-title {
  margin-bottom: 13px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chunk-preview-header h5,
.detail-title h5 {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
}

.chunk-preview-header span,
.detail-title span {
  padding: 5px 10px;
  border-radius: 20px;
  color: #4338ca;
  background: #eef2ff;
  font-size: 11px;
  font-weight: 700;
}

.chunk-preview-item {
  margin-bottom: 9px;
  padding: 11px;
  border-radius: 9px;
  background: white;
}

.chunk-preview-item strong {
  color: #4338ca;
  font-size: 12px;
}

.chunk-preview-item p {
  margin: 5px 0 0;
  color: #4b5563;
  font-size: 13px;
}

.more-chunks {
  color: #6b7280;
}

.full-content {
  margin-bottom: 22px;
  padding: 17px;
  border-radius: 13px;
  background: #f8fafc;
}

.full-content h5 {
  margin: 0 0 10px;
  font-weight: 700;
  font-size: 15px;
}

.full-content p {
  margin: 0;
  color: #4b5563;
  line-height: 1.7;
}

.chunk-detail-item {
  margin-bottom: 10px;
  padding: 13px;
  border: 1px solid #edf0f5;
  border-radius: 11px;
  display: flex;
  gap: 12px;
}

.chunk-number {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: 50%;
  color: white;
  background: #6366f1;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 12px;
  font-weight: 700;
}

.chunk-detail-item p {
  margin: 3px 0 0;
  color: #4b5563;
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
  .document-heading,
  .source-type-box {
    flex-direction: column;
    align-items: flex-start;
  }

  .filters,
  .search-box,
  .filters select {
    width: 100%;
  }

  .document-card {
    flex-direction: column;
  }
}
</style>