<template>
	<div class="tasks-page">
		<div class="page-header">
			<div>
				<h2>Bài tập</h2>
				<p>Theo dõi deadline, trạng thái và mức độ ưu tiên của từng bài tập.</p>
			</div>

			<button class="add-btn" @click="openAddModal">
				<i class="bi bi-plus-lg"></i>
				Thêm bài tập
			</button>
		</div>

		<div class="summary-grid">
			<div class="summary-card">
				<div class="summary-icon total">
					<i class="bi bi-list-check"></i>
				</div>
				<div>
					<p>Tổng bài tập</p>
					<h3>{{ tasks.length }}</h3>
				</div>
			</div>

			<div class="summary-card">
				<div class="summary-icon pending">
					<i class="bi bi-hourglass-split"></i>
				</div>
				<div>
					<p>Chưa hoàn thành</p>
					<h3>{{ unfinishedCount }}</h3>
				</div>
			</div>

			<div class="summary-card">
				<div class="summary-icon urgent">
					<i class="bi bi-exclamation-triangle"></i>
				</div>
				<div>
					<p>Ưu tiên cao</p>
					<h3>{{ highPriorityCount }}</h3>
				</div>
			</div>

			<div class="summary-card">
				<div class="summary-icon done">
					<i class="bi bi-check-circle"></i>
				</div>
				<div>
					<p>Đã hoàn thành</p>
					<h3>{{ completedCount }}</h3>
				</div>
			</div>
		</div>

		<div class="content-card">
			<div class="toolbar">
				<div>
					<h5>Danh sách bài tập</h5>
					<p>Dữ liệu được lấy trực tiếp từ MariaDB.</p>
				</div>

				<div class="filter-area">
					<div class="search-box">
						<i class="bi bi-search"></i>
						<input v-model="searchKeyword" type="text" placeholder="Tìm bài tập..." />
					</div>

					<select v-model="selectedSubject" class="filter-select">
						<option value="">Tất cả môn học</option>
						<option v-for="subject in subjects" :key="subject.id" :value="subject.id">
							{{ subject.name }}
						</option>
					</select>

					<select v-model="selectedStatus" class="filter-select">
						<option value="">Tất cả trạng thái</option>
						<option value="CHUA_LAM">Chưa làm</option>
						<option value="DANG_LAM">Đang làm</option>
						<option value="HOAN_THANH">Đã hoàn thành</option>
					</select>
				</div>
			</div>

			<div v-if="isLoading" class="loading-state">
				<span class="loading-spinner"></span>
				<p>Đang tải danh sách bài tập...</p>
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

			<div v-else-if="filteredTasks.length === 0" class="empty-state">
				<div class="empty-icon">
					<i class="bi bi-journal-check"></i>
				</div>

				<h5>Chưa có bài tập nào</h5>
				<p>Hãy thêm bài tập đầu tiên để theo dõi deadline và mức độ ưu tiên.</p>

				<button class="add-btn" @click="openAddModal">
					<i class="bi bi-plus-lg"></i>
					Thêm bài tập
				</button>
			</div>

			<div v-else class="task-list">
				<div v-for="task in filteredTasks" :key="task.id" class="task-card" :class="task.priorityClass">
					<div class="task-main">
						<div class="priority-line">
							<span class="priority-badge" :class="task.priorityClass">
								{{ task.priorityLabel }}
							</span>

							<span class="score-badge">
								Điểm: {{ task.priorityScore }}
							</span>
						</div>

						<h5>{{ task.title }}</h5>

						<p class="task-description">
							{{ task.description || 'Không có mô tả.' }}
						</p>

						<div class="task-meta">
							<span>
								<i class="bi bi-book"></i>
								{{ task.subjectName }}
							</span>

							<span>
								<i class="bi bi-calendar-event"></i>
								{{ formatDateTime(task.deadline) }}
							</span>

							<span>
								<i class="bi bi-bar-chart"></i>
								Độ khó {{ task.difficulty }}/5
							</span>

							<span>
								<i class="bi bi-star"></i>
								Quan trọng {{ task.importance }}/5
							</span>
						</div>
					</div>

					<div class="task-side">
						<select class="status-select" :class="task.status" :value="task.status"
							@change="changeStatus(task, $event.target.value)">
							<option value="CHUA_LAM">Chưa làm</option>
							<option value="DANG_LAM">Đang làm</option>
							<option value="HOAN_THANH">Đã hoàn thành</option>
						</select>

						<div class="action-group">
							<button class="action-btn edit" @click="openEditModal(task)">
								<i class="bi bi-pencil-square"></i>
							</button>

							<button class="action-btn delete" @click="confirmDelete(task)">
								<i class="bi bi-trash"></i>
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Modal thêm/sửa -->
		<div v-if="isModalOpen" class="modal-overlay">
			<div class="modal-card">
				<div class="modal-header-custom">
					<div>
						<h4>{{ isEditing ? 'Cập nhật bài tập' : 'Thêm bài tập mới' }}</h4>
						<p>Nhập thông tin bài tập, deadline và mức độ ưu tiên.</p>
					</div>

					<button class="close-btn" @click="closeModal">
						<i class="bi bi-x-lg"></i>
					</button>
				</div>

				<form @submit.prevent="saveTask">
					<div class="form-group">
						<label>Môn học <span>*</span></label>
						<select v-model="form.subjectId" :class="{ invalid: errors.subjectId }">
							<option value="">Chọn môn học</option>
							<option v-for="subject in subjects" :key="subject.id" :value="subject.id">
								{{ subject.name }}
							</option>
						</select>
						<small v-if="errors.subjectId" class="error-text">
							{{ errors.subjectId }}
						</small>
					</div>

					<div class="form-group">
						<label>Tiêu đề bài tập <span>*</span></label>
						<input v-model="form.title" type="text" placeholder="Ví dụ: Hoàn thành API FastAPI"
							:class="{ invalid: errors.title }" />
						<small v-if="errors.title" class="error-text">
							{{ errors.title }}
						</small>
					</div>

					<div class="form-group">
						<label>Mô tả</label>
						<textarea v-model="form.description" rows="3" placeholder="Mô tả ngắn về bài tập..."></textarea>
					</div>

					<div class="row g-3">
						<div class="col-md-6">
							<div class="form-group">
								<label>Deadline <span>*</span></label>
								<input v-model="form.deadline" type="datetime-local"
									:class="{ invalid: errors.deadline }" />
								<small v-if="errors.deadline" class="error-text">
									{{ errors.deadline }}
								</small>
							</div>
						</div>

						<div class="col-md-6">
							<div class="form-group">
								<label>Trạng thái</label>
								<select v-model="form.status">
									<option value="CHUA_LAM">Chưa làm</option>
									<option value="DANG_LAM">Đang làm</option>
									<option value="HOAN_THANH">Đã hoàn thành</option>
								</select>
							</div>
						</div>
					</div>

					<div class="row g-3">
						<div class="col-md-6">
							<div class="form-group">
								<label>Độ khó: {{ form.difficulty }}/5</label>
								<input v-model.number="form.difficulty" type="range" min="1" max="5" />
							</div>
						</div>

						<div class="col-md-6">
							<div class="form-group">
								<label>Mức độ quan trọng: {{ form.importance }}/5</label>
								<input v-model.number="form.importance" type="range" min="1" max="5" />
							</div>
						</div>
					</div>

					<div class="modal-footer-custom">
						<button type="button" class="cancel-btn" @click="closeModal">
							Hủy
						</button>

						<button type="submit" class="save-btn" :disabled="isSaving">
							<template v-if="!isSaving">
								<i class="bi bi-check-lg"></i>
								{{ isEditing ? 'Lưu thay đổi' : 'Thêm bài tập' }}
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

		<!-- Modal xóa -->
		<div v-if="taskToDelete" class="modal-overlay">
			<div class="delete-modal">
				<div class="delete-icon">
					<i class="bi bi-trash"></i>
				</div>

				<h4>Xóa bài tập?</h4>
				<p>
					Bạn có chắc muốn xóa
					<strong>{{ taskToDelete.title }}</strong>
					không?
				</p>

				<div class="delete-actions">
					<button class="cancel-btn" @click="taskToDelete = null">
						Hủy
					</button>

					<button class="confirm-delete-btn" :disabled="isDeleting" @click="deleteTask">
						{{ isDeleting ? 'Đang xóa...' : 'Xóa bài tập' }}
					</button>
				</div>
			</div>
		</div>

		<div v-if="toast.message" class="toast-message" :class="toast.type">
			<i class="bi" :class="toast.type === 'success' ? 'bi-check-circle' : 'bi-exclamation-circle'"></i>
			{{ toast.message }}
		</div>
	</div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const tasks = ref([])
const subjects = ref([])

const searchKeyword = ref('')
const selectedSubject = ref('')
const selectedStatus = ref('')

const isLoading = ref(false)
const isSaving = ref(false)
const isDeleting = ref(false)
const apiError = ref('')

const isModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const taskToDelete = ref(null)

const toast = ref({
	message: '',
	type: 'success',
})

const emptyForm = () => ({
	subjectId: '',
	title: '',
	description: '',
	deadline: '',
	difficulty: 3,
	importance: 3,
	status: 'CHUA_LAM',
})

const form = ref(emptyForm())

const errors = ref({
	subjectId: '',
	title: '',
	deadline: '',
})

const statusLabels = {
	CHUA_LAM: 'Chưa làm',
	DANG_LAM: 'Đang làm',
	HOAN_THANH: 'Đã hoàn thành',
}

const unfinishedCount = computed(() => {
	return tasks.value.filter((task) => task.status !== 'HOAN_THANH').length
})

const completedCount = computed(() => {
	return tasks.value.filter((task) => task.status === 'HOAN_THANH').length
})

const highPriorityCount = computed(() => {
	return tasks.value.filter((task) =>
		['very-high', 'high', 'overdue'].includes(task.priorityClass),
	).length
})

const filteredTasks = computed(() => {
	const keyword = searchKeyword.value.trim().toLowerCase()

	return tasks.value.filter((task) => {
		const matchedKeyword =
			task.title.toLowerCase().includes(keyword) ||
			task.subjectName.toLowerCase().includes(keyword) ||
			(task.description || '').toLowerCase().includes(keyword)

		const matchedSubject =
			!selectedSubject.value ||
			Number(task.subjectId) === Number(selectedSubject.value)

		const matchedStatus =
			!selectedStatus.value || task.status === selectedStatus.value

		return matchedKeyword && matchedSubject && matchedStatus
	})
})

const mapTaskFromApi = (task) => ({
	id: task.id,
	subjectId: task.subject_id,
	subjectName: task.subject_name,
	title: task.title,
	description: task.description || '',
	deadline: task.deadline,
	difficulty: task.difficulty,
	importance: task.importance,
	status: task.status,
	statusLabel: statusLabels[task.status] || task.status,
	completedAt: task.completed_at,
	priorityScore: task.priority_score,
	priorityLabel: task.priority_label,
	priorityClass: task.priority_class,
	createdAt: task.created_at,
	updatedAt: task.updated_at,
})

const mapSubjectFromApi = (subject) => ({
	id: subject.id,
	name: subject.name,
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

const loadInitialData = async () => {
	isLoading.value = true
	apiError.value = ''

	try {
		await Promise.all([fetchSubjects(), fetchTasks()])
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
		subjectId: '',
		title: '',
		deadline: '',
	}
}

const openAddModal = () => {
	isEditing.value = false
	editingId.value = null
	form.value = {
		...emptyForm(),
		subjectId: subjects.value[0]?.id || '',
	}

	resetErrors()
	isModalOpen.value = true
}

const openEditModal = (task) => {
	isEditing.value = true
	editingId.value = task.id

	form.value = {
		subjectId: task.subjectId,
		title: task.title,
		description: task.description,
		deadline: toDatetimeLocal(task.deadline),
		difficulty: task.difficulty,
		importance: task.importance,
		status: task.status,
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

	if (!form.value.subjectId) {
		errors.value.subjectId = 'Vui lòng chọn môn học.'
		valid = false
	}

	if (!form.value.title.trim()) {
		errors.value.title = 'Vui lòng nhập tiêu đề bài tập.'
		valid = false
	}

	if (!form.value.deadline) {
		errors.value.deadline = 'Vui lòng chọn deadline.'
		valid = false
	}

	return valid
}

const buildPayload = () => ({
	subject_id: Number(form.value.subjectId),
	title: form.value.title.trim(),
	description: form.value.description.trim() || null,
	deadline: form.value.deadline,
	difficulty: Number(form.value.difficulty),
	importance: Number(form.value.importance),
	status: form.value.status,
})

const saveTask = async () => {
	if (!validateForm()) return

	isSaving.value = true

	try {
		if (isEditing.value) {
			const response = await api.put(`/tasks/${editingId.value}`, buildPayload())
			const updatedTask = mapTaskFromApi(response.data)

			const index = tasks.value.findIndex((task) => task.id === editingId.value)

			if (index !== -1) {
				tasks.value[index] = updatedTask
			}

			showToast('Cập nhật bài tập thành công.')
		} else {
			const response = await api.post('/tasks', buildPayload())
			tasks.value.unshift(mapTaskFromApi(response.data))
			showToast('Thêm bài tập thành công.')
		}

		closeModal()
	} catch (error) {
		showToast(
			handleApiError(error, 'Không thể lưu bài tập. Vui lòng thử lại.'),
			'error',
		)
	} finally {
		isSaving.value = false
	}
}

const changeStatus = async (task, newStatus) => {
	try {
		const response = await api.patch(`/tasks/${task.id}/status`, {
			status: newStatus,
		})

		const updatedTask = mapTaskFromApi(response.data)
		const index = tasks.value.findIndex((item) => item.id === task.id)

		if (index !== -1) {
			tasks.value[index] = updatedTask
		}

		showToast('Cập nhật trạng thái thành công.')
	} catch (error) {
		showToast(
			handleApiError(error, 'Không thể cập nhật trạng thái.'),
			'error',
		)
	}
}

const confirmDelete = (task) => {
	taskToDelete.value = task
}

const deleteTask = async () => {
	if (!taskToDelete.value) return

	isDeleting.value = true

	try {
		await api.delete(`/tasks/${taskToDelete.value.id}`)

		tasks.value = tasks.value.filter(
			(task) => task.id !== taskToDelete.value.id,
		)

		taskToDelete.value = null
		showToast('Xóa bài tập thành công.')
	} catch (error) {
		showToast(
			handleApiError(error, 'Không thể xóa bài tập.'),
			'error',
		)
	} finally {
		isDeleting.value = false
	}
}

const toDatetimeLocal = (value) => {
	if (!value) return ''

	const date = new Date(value)
	const offset = date.getTimezoneOffset()
	const localDate = new Date(date.getTime() - offset * 60 * 1000)

	return localDate.toISOString().slice(0, 16)
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

onMounted(() => {
	loadInitialData()
})
</script>

<style scoped>
.tasks-page {
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

.add-btn {
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

.add-btn:hover {
	background: linear-gradient(135deg, var(--sm-primary-dark), var(--sm-primary));
	transform: translateY(-1px);
}

.summary-grid {
	margin-bottom: 24px;
	display: grid;
	grid-template-columns: repeat(4, 1fr);
	gap: 18px;
}

.summary-card {
	min-height: 108px;
	padding: 21px;
	border: 1px solid var(--sm-border);
	border-radius: 18px;
	background: var(--sm-card);
	box-shadow: var(--sm-shadow-sm);
	display: flex;
	align-items: center;
	gap: 16px;
}

.summary-icon {
	width: 54px;
	height: 54px;
	border-radius: 15px;
	font-size: 24px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.summary-icon.total {
	color: var(--sm-primary);
	background: var(--sm-primary-soft);
}

.summary-icon.pending {
	color: var(--sm-warning);
	background: var(--sm-warning-bg);
}

.summary-icon.urgent {
	color: var(--sm-danger);
	background: var(--sm-danger-bg);
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
	align-items: center;
	justify-content: space-between;
	gap: 22px;
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

.filter-area {
	display: flex;
	gap: 12px;
}

.search-box {
	width: 250px;
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

.filter-select {
	height: 44px;
	min-width: 150px;
	padding: 0 13px;
	border: 1px solid var(--sm-border);
	border-radius: 11px;
	outline: none;
	color: var(--sm-text);
	background: #fffdfa;
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
.empty-state p,
.api-error-state p {
	margin-top: 16px;
	color: var(--sm-text-soft);
}

.empty-icon,
.error-api-icon {
	width: 66px;
	height: 66px;
	margin: 0 auto 18px;
	border-radius: 50%;
	font-size: 31px;
	display: flex;
	align-items: center;
	justify-content: center;
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

.task-list {
	display: flex;
	flex-direction: column;
	gap: 14px;
}

.task-card {
	padding: 18px;
	border: 1px solid var(--sm-border);
	border-left: 5px solid var(--sm-primary);
	border-radius: 16px;
	background: #fffdfa;
	display: flex;
	justify-content: space-between;
	gap: 18px;
}

.task-card.overdue {
	border-left-color: var(--sm-danger);
}

.task-card.very-high,
.task-card.high {
	border-left-color: var(--sm-warning);
}

.task-card.completed {
	opacity: 0.76;
	border-left-color: var(--sm-success);
}

.priority-line {
	margin-bottom: 10px;
	display: flex;
	gap: 8px;
	flex-wrap: wrap;
}

.priority-badge,
.score-badge {
	padding: 6px 10px;
	border-radius: 999px;
	font-size: 12px;
	font-weight: 700;
}

.priority-badge.overdue {
	color: var(--sm-danger);
	background: var(--sm-danger-bg);
}

.priority-badge.very-high,
.priority-badge.high {
	color: var(--sm-warning);
	background: var(--sm-warning-bg);
}

.priority-badge.medium {
	color: var(--sm-primary-dark);
	background: var(--sm-primary-soft);
}

.priority-badge.low {
	color: var(--sm-success);
	background: var(--sm-success-bg);
}

.priority-badge.completed {
	color: var(--sm-success);
	background: var(--sm-success-bg);
}

.score-badge {
	color: var(--sm-text-soft);
	background: #f5eee5;
}

.task-main h5 {
	margin: 0 0 8px;
	color: var(--sm-text);
	font-weight: 700;
}

.task-description {
	margin: 0 0 14px;
	color: var(--sm-text-soft);
	line-height: 1.6;
}

.task-meta {
	display: flex;
	flex-wrap: wrap;
	gap: 10px 16px;
}

.task-meta span {
	color: #786b60;
	font-size: 13px;
}

.task-meta i {
	margin-right: 5px;
	color: var(--sm-primary);
}

.task-side {
	min-width: 170px;
	display: flex;
	flex-direction: column;
	align-items: flex-end;
	gap: 13px;
}

.status-select {
	height: 39px;
	padding: 0 10px;
	border: 1px solid var(--sm-border);
	border-radius: 10px;
	outline: none;
	font-size: 13px;
	font-weight: 600;
	background: #fffdfa;
}

.status-select.CHUA_LAM {
	color: var(--sm-warning);
}

.status-select.DANG_LAM {
	color: var(--sm-primary-dark);
}

.status-select.HOAN_THANH {
	color: var(--sm-success);
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

.modal-overlay {
	position: fixed;
	inset: 0;
	z-index: 300;
	padding: 22px;
	background: rgba(48, 40, 33, 0.48);
	backdrop-filter: blur(3px);
	display: flex;
	align-items: center;
	justify-content: center;
}

.modal-card {
	width: 650px;
	max-width: 100%;
	max-height: 93vh;
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

@media (max-width: 1100px) {
	.summary-grid {
		grid-template-columns: repeat(2, 1fr);
	}

	.toolbar {
		flex-direction: column;
		align-items: flex-start;
	}

	.filter-area {
		width: 100%;
		flex-direction: column;
	}

	.search-box,
	.filter-select {
		width: 100%;
	}
}

@media (max-width: 760px) {
	.page-header {
		flex-direction: column;
		align-items: flex-start;
		gap: 15px;
	}

	.summary-grid {
		grid-template-columns: 1fr;
	}

	.task-card {
		flex-direction: column;
	}

	.task-side {
		width: 100%;
		min-width: 0;
		align-items: flex-start;
	}
}
</style>