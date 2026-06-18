<template>
    <div class="subjects-page">
        <!-- Tiêu đề trang -->
        <div class="page-header">
            <div>
                <h2>Môn học</h2>
                <p>Danh sách các môn học bạn đang theo dõi trong học kỳ này.</p>
            </div>

            <button class="add-btn" @click="openAddModal">
                <i class="bi bi-plus-lg"></i>
                Thêm môn học
            </button>
        </div>

        <!-- Thống kê nhanh -->
        <div class="row g-4 mb-4">
            <div class="col-xl-4 col-md-6">
                <div class="summary-card">
                    <div class="summary-icon purple">
                        <i class="bi bi-book-fill"></i>
                    </div>

                    <div>
                        <p>Tổng số môn học</p>
                        <h3>{{ subjects.length }}</h3>
                    </div>
                </div>
            </div>

            <div class="col-xl-4 col-md-6">
                <div class="summary-card">
                    <div class="summary-icon blue">
                        <i class="bi bi-calendar3"></i>
                    </div>

                    <div>
                        <p>Học kỳ hiện tại</p>
                        <h3>{{ currentSemester }}</h3>
                    </div>
                </div>
            </div>

            <div class="col-xl-4 col-md-6">
                <div class="summary-card">
                    <div class="summary-icon green">
                        <i class="bi bi-check-circle-fill"></i>
                    </div>

                    <div>
                        <p>Môn đã có tài liệu</p>
                        <h3>{{ subjectsWithDocuments }}</h3>
                    </div>
                </div>
            </div>
        </div>

        <!-- Danh sách môn học -->
        <div class="content-card">
            <div class="toolbar">
                <div>
                    <h5>Danh sách môn học</h5>
                    <p>Quản lý thông tin từng môn học của bạn</p>
                </div>

                <div class="filter-area">
                    <div class="search-box">
                        <i class="bi bi-search"></i>
                        <input v-model="searchKeyword" type="text" placeholder="Tìm theo tên hoặc mã môn..." />
                    </div>

                    <select v-model="selectedSemester" class="semester-select">
                        <option value="">Tất cả học kỳ</option>
                        <option value="HK1">HK1</option>
                        <option value="HK2">HK2</option>
                        <option value="HK3">HK HÈ</option>
                    </select>
                </div>
            </div>

            <!-- Đang tải dữ liệu -->
            <div v-if="isLoading" class="loading-state">
                <span class="loading-spinner"></span>
                <p>Đang tải danh sách môn học...</p>
            </div>

            <!-- Lỗi kết nối API -->
            <div v-else-if="apiError" class="api-error-state">
                <div class="error-api-icon">
                    <i class="bi bi-exclamation-circle"></i>
                </div>

                <h5>Không thể tải dữ liệu</h5>
                <p>{{ apiError }}</p>

                <button class="retry-btn" @click="fetchSubjects">
                    <i class="bi bi-arrow-clockwise"></i>
                    Thử lại
                </button>
            </div>

            <!-- Khi chưa có dữ liệu -->
            <div v-if="filteredSubjects.length === 0" class="empty-state">
                <div class="empty-icon">
                    <i class="bi bi-journal-x"></i>
                </div>

                <h5>Chưa tìm thấy môn học</h5>
                <p>Hãy thêm môn học mới hoặc thay đổi từ khóa tìm kiếm.</p>

                <button class="add-btn" @click="openAddModal">
                    <i class="bi bi-plus-lg"></i>
                    Thêm môn học
                </button>
            </div>

            <!-- Table danh sách -->
            <div v-else class="table-responsive">
                <table class="subject-table">
                    <thead>
                        <tr>
                            <th>Môn học</th>
                            <th>Mã môn</th>
                            <th>Học kỳ</th>
                            <th>Năm học</th>
                            <th>Tài liệu</th>
                            <th class="text-center">Thao tác</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="subject in filteredSubjects" :key="subject.id">
                            <td>
                                <div class="subject-info">
                                    <span class="subject-color" :style="{ backgroundColor: subject.color }"></span>

                                    <div>
                                        <p class="subject-name">{{ subject.name }}</p>
                                        <small>{{ subject.description || 'Chưa có mô tả' }}</small>
                                    </div>
                                </div>
                            </td>

                            <td>
                                <span class="code-badge">{{ subject.code || '---' }}</span>
                            </td>

                            <td>{{ formatSemester(subject.semester) }}</td>

                            <td>{{ subject.academicYear || '---' }}</td>

                            <td>
                                <span class="document-badge" :class="subject.hasDocuments ? 'active' : 'inactive'">
                                    <i :class="subject.hasDocuments
                                        ? 'bi bi-check-circle-fill'
                                        : 'bi bi-dash-circle'
                                        "></i>

                                    {{ subject.hasDocuments ? 'Đã có' : 'Chưa có' }}
                                </span>
                            </td>

                            <td>
                                <div class="action-group">
                                    <button class="action-btn view" title="Xem tài liệu"
                                        @click="goToDocuments(subject)">
                                        <i class="bi bi-file-earmark-text"></i>
                                    </button>

                                    <button class="action-btn edit" title="Sửa môn học" @click="openEditModal(subject)">
                                        <i class="bi bi-pencil-square"></i>
                                    </button>

                                    <button class="action-btn delete" title="Xóa môn học"
                                        @click="confirmDelete(subject)">
                                        <i class="bi bi-trash3"></i>
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Modal thêm/sửa môn học -->
        <div v-if="isModalOpen" class="modal-overlay" @click.self="closeModal">
            <div class="modal-card">
                <div class="modal-header-custom">
                    <div>
                        <h4>{{ isEditing ? 'Cập nhật môn học' : 'Thêm môn học mới' }}</h4>
                        <p>Nhập thông tin môn học để theo dõi học tập.</p>
                    </div>

                    <button class="close-btn" @click="closeModal">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>

                <form @submit.prevent="saveSubject">
                    <div class="form-group">
                        <label>Tên môn học <span>*</span></label>
                        <input v-model.trim="form.name" type="text" placeholder="Ví dụ: Perl & Python"
                            :class="{ invalid: errors.name }" />
                        <small v-if="errors.name" class="error-text">
                            {{ errors.name }}
                        </small>
                    </div>

                    <div class="row g-3">
                        <div class="col-md-4">
                            <div class="form-group">
                                <label>Mã môn</label>
                                <input v-model.trim="form.code" type="text" placeholder="CS466" />
                            </div>
                        </div>

                        <div class="col-md-4">
                            <div class="form-group">
                                <label>Học kỳ <span>*</span></label>
                                <select v-model="form.semester" :class="{ invalid: errors.semester }">
                                    <option value="">Chọn học kỳ</option>
                                    <option value="HK1">HK1</option>
                                    <option value="HK2">HK2</option>
                                    <option value="HK3">HK HÈ</option>
                                </select>
                                <small v-if="errors.semester" class="error-text">
                                    {{ errors.semester }}
                                </small>
                            </div>
                        </div>

                        <div class="col-md-4">
                            <div class="form-group">
                                <label>Năm học <span>*</span></label>
                                <input v-model.trim="form.academicYear" type="text" placeholder="2025-2026"
                                    :class="{ invalid: errors.academicYear }" />
                                <small v-if="errors.academicYear" class="error-text">
                                    {{ errors.academicYear }}
                                </small>
                            </div>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Màu hiển thị</label>

                        <div class="color-list">
                            <button v-for="color in subjectColors" :key="color" type="button" class="color-option"
                                :class="{ selected: form.color === color }" :style="{ backgroundColor: color }"
                                @click="form.color = color">
                                <i v-if="form.color === color" class="bi bi-check-lg"></i>
                            </button>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>Mô tả môn học</label>
                        <textarea v-model.trim="form.description" rows="3"
                            placeholder="Nhập nội dung mô tả ngắn về môn học..."></textarea>
                    </div>


                    <div class="modal-footer-custom">
                        <button type="button" class="cancel-btn" @click="closeModal">
                            Hủy
                        </button>

                        <button type="submit" class="save-btn" :disabled="isSaving">
                            <template v-if="!isSaving">
                                <i class="bi bi-check-lg"></i>
                                {{ isEditing ? 'Lưu thay đổi' : 'Thêm môn học' }}
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

        <!-- Modal xác nhận xóa -->
        <div v-if="subjectToDelete" class="modal-overlay" @click.self="subjectToDelete = null">
            <div class="delete-modal">
                <div class="delete-icon">
                    <i class="bi bi-trash3"></i>
                </div>

                <h4>Xóa môn học?</h4>
                <p>
                    Bạn có chắc muốn xóa môn
                    <strong>{{ subjectToDelete.name }}</strong> không?
                </p>

                <div class="delete-actions">
                    <button class="cancel-btn" @click="subjectToDelete = null">
                        Hủy
                    </button>

                    <button class="confirm-delete-btn" :disabled="isDeleting" @click="deleteSubject">
                        {{ isDeleting ? 'Đang xóa...' : 'Xóa môn học' }}
                    </button>
                </div>
            </div>
        </div>

        <!-- Thông báo nhỏ -->
        <div v-if="toast.message" class="toast-message" :class="toast.type">
            <i :class="toast.type === 'success'
                ? 'bi bi-check-circle-fill'
                : 'bi bi-exclamation-circle-fill'
                "></i>
            {{ toast.message }}
        </div>
    </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'

const router = useRouter()

const subjects = ref([])
const searchKeyword = ref('')
const selectedSemester = ref('')

const isLoading = ref(false)
const isSaving = ref(false)
const isDeleting = ref(false)
const apiError = ref('')

const isModalOpen = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const subjectToDelete = ref(null)

const toast = ref({
    message: '',
    type: 'success',
})

const subjectColors = [
    '#B9824C',
    '#D6A86E',
    '#8A6748',
    '#C98242',
    '#72825B',
    '#B55A49',
]

const emptyForm = () => ({
    name: '',
    code: '',
    semester: 'HK3',
    academicYear: '2025-2026',
    description: '',
    color: '#B9824C',
})

const form = ref(emptyForm())

const errors = ref({
    name: '',
    semester: '',
    academicYear: '',
})

const formatSemester = (semester) => {
    if (semester === 'HK3') {
        return 'HK HÈ'
    }

    return semester || '---'
}

const currentSemester = computed(() => {
    if (subjects.value.length === 0) {
        return 'HK HÈ'
    }

    return formatSemester(subjects.value[0]?.semester)
})

const filteredSubjects = computed(() => {
    const keyword = searchKeyword.value.trim().toLowerCase()

    return subjects.value.filter((subject) => {
        const matchedKeyword =
            subject.name.toLowerCase().includes(keyword) ||
            (subject.code || '').toLowerCase().includes(keyword)

        const matchedSemester =
            !selectedSemester.value || subject.semester === selectedSemester.value

        return matchedKeyword && matchedSemester
    })
})

const subjectsWithDocuments = computed(() => {
    return subjects.value.filter((subject) => subject.hasDocuments).length
})

const mapSubjectFromApi = (subject) => ({
    id: subject.id,
    userId: subject.user_id,
    name: subject.name,
    code: subject.code || '',
    semester: subject.semester || '',
    academicYear: subject.academic_year || '',
    description: subject.description || '',
    color: subject.color || '#B9824C',
    hasDocuments: subject.has_documents || false,
    createdAt: subject.created_at,
    updatedAt: subject.updated_at,
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
    isLoading.value = true
    apiError.value = ''

    try {
        const response = await api.get('/subjects')
        subjects.value = response.data.map(mapSubjectFromApi)
    } catch (error) {
        apiError.value = handleApiError(
            error,
            'Không thể kết nối đến hệ thống. Vui lòng thử lại.',
        )
    } finally {
        isLoading.value = false
    }
}

const resetErrors = () => {
    errors.value = {
        name: '',
        semester: '',
        academicYear: '',
    }
}

const openAddModal = () => {
    isEditing.value = false
    editingId.value = null
    form.value = emptyForm()
    resetErrors()
    isModalOpen.value = true
}

const openEditModal = (subject) => {
    isEditing.value = true
    editingId.value = subject.id

    form.value = {
        name: subject.name,
        code: subject.code,
        semester: subject.semester,
        academicYear: subject.academicYear,
        description: subject.description,
        color: subject.color,
    }

    resetErrors()
    isModalOpen.value = true
}

const closeModal = () => {
    if (isSaving.value) {
        return
    }

    isModalOpen.value = false
    resetErrors()
}

const validateForm = () => {
    resetErrors()
    let isValid = true

    if (!form.value.name.trim()) {
        errors.value.name = 'Vui lòng nhập tên môn học.'
        isValid = false
    }

    if (!form.value.semester) {
        errors.value.semester = 'Vui lòng chọn học kỳ.'
        isValid = false
    }

    if (!form.value.academicYear.trim()) {
        errors.value.academicYear = 'Vui lòng nhập năm học.'
        isValid = false
    }

    return isValid
}

const buildPayload = () => ({
    name: form.value.name.trim(),
    code: form.value.code.trim() || null,
    semester: form.value.semester || null,
    academic_year: form.value.academicYear.trim() || null,
    description: form.value.description.trim() || null,
    color: form.value.color || '#B9824C',
})

const saveSubject = async () => {
    if (!validateForm()) {
        return
    }

    isSaving.value = true

    try {
        if (isEditing.value) {
            const response = await api.put(
                `/subjects/${editingId.value}`,
                buildPayload(),
            )

            const updatedSubject = mapSubjectFromApi(response.data)
            const index = subjects.value.findIndex(
                (subject) => subject.id === editingId.value,
            )

            if (index !== -1) {
                subjects.value[index] = updatedSubject
            }

            showToast('Cập nhật môn học thành công.')
        } else {
            const response = await api.post('/subjects', buildPayload())
            subjects.value.unshift(mapSubjectFromApi(response.data))
            showToast('Thêm môn học thành công.')
        }

        closeModal()
    } catch (error) {
        const message = handleApiError(
            error,
            'Không thể lưu môn học. Vui lòng thử lại.',
        )

        if (error.response?.status === 409) {
            errors.value.name = message
        } else {
            showToast(message, 'error')
        }
    } finally {
        isSaving.value = false
        isModalOpen.value = false
    }
}

const confirmDelete = (subject) => {
    subjectToDelete.value = subject
}

const deleteSubject = async () => {
    if (!subjectToDelete.value) {
        return
    }

    isDeleting.value = true

    try {
        await api.delete(`/subjects/${subjectToDelete.value.id}`)

        subjects.value = subjects.value.filter(
            (subject) => subject.id !== subjectToDelete.value.id,
        )

        subjectToDelete.value = null
        showToast('Đã xóa môn học thành công.')
    } catch (error) {
        showToast(
            handleApiError(error, 'Không thể xóa môn học. Vui lòng thử lại.'),
            'error',
        )
    } finally {
        isDeleting.value = false
    }
}

const goToDocuments = (subject) => {
    router.push({
        path: '/tai-lieu',
        query: {
            subject: subject.id,
            name: subject.name,
        },
    })
}

onMounted(() => {
    fetchSubjects()
})
</script>

<style scoped>
.subjects-page {
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

.summary-icon.purple {
    color: var(--sm-primary);
    background: var(--sm-primary-soft);
}

.summary-icon.blue {
    color: #9b713f;
    background: #fbf0e2;
}

.summary-icon.green {
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
    width: 280px;
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

.search-box input::placeholder {
    color: var(--sm-text-muted);
}

.semester-select {
    height: 44px;
    min-width: 150px;
    padding: 0 13px;
    border: 1px solid var(--sm-border);
    border-radius: 11px;
    outline: none;
    color: var(--sm-text);
    background: #fffdfa;
}

.semester-select:focus {
    border-color: #d8b992;
}

.loading-state,
.api-error-state,
.empty-state {
    padding: 56px 20px;
    text-align: center;
}

.loading-state p {
    margin: 18px 0 0;
    color: var(--sm-text-soft);
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

.error-api-icon,
.empty-icon {
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

.empty-state h5,
.api-error-state h5 {
    color: var(--sm-text);
    font-weight: 700;
}

.empty-state p,
.api-error-state p {
    margin-bottom: 22px;
    color: var(--sm-text-soft);
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

.subject-table {
    width: 100%;
    border-collapse: collapse;
}

.subject-table th {
    padding: 14px 16px;
    color: var(--sm-text-soft);
    background: #f7f0e8;
    font-size: 13px;
    font-weight: 600;
    text-align: left;
}

.subject-table th:first-child {
    border-radius: 11px 0 0 11px;
}

.subject-table th:last-child {
    border-radius: 0 11px 11px 0;
}

.subject-table td {
    padding: 17px 16px;
    border-bottom: 1px solid #f2e8dd;
    color: #574a41;
    vertical-align: middle;
}

.subject-info {
    display: flex;
    align-items: center;
    gap: 13px;
}

.subject-color {
    width: 10px;
    height: 48px;
    border-radius: 20px;
}

.subject-name {
    margin: 0 0 4px;
    color: var(--sm-text);
    font-weight: 600;
}

.subject-info small {
    color: var(--sm-text-soft);
}

.code-badge {
    padding: 7px 12px;
    border-radius: 9px;
    color: var(--sm-primary-dark);
    background: var(--sm-primary-soft);
    font-size: 13px;
    font-weight: 600;
}

.document-badge {
    padding: 7px 11px;
    border-radius: 22px;
    font-size: 13px;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

.document-badge.active {
    color: var(--sm-success);
    background: var(--sm-success-bg);
}

.document-badge.inactive {
    color: var(--sm-text-soft);
    background: #f4ede5;
}

.action-group {
    display: flex;
    justify-content: center;
    gap: 8px;
}

.action-btn {
    width: 37px;
    height: 37px;
    border: none;
    border-radius: 9px;
    background: transparent;
}

.action-btn.view {
    color: var(--sm-primary-dark);
    background: var(--sm-primary-soft);
}

.action-btn.edit {
    color: var(--sm-warning);
    background: var(--sm-warning-bg);
}

.action-btn.delete {
    color: var(--sm-danger);
    background: var(--sm-danger-bg);
}

.action-btn:hover {
    transform: translateY(-1px);
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
    width: 620px;
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

.color-list {
    display: flex;
    gap: 12px;
}

.color-option {
    width: 35px;
    height: 35px;
    border: 3px solid transparent;
    border-radius: 50%;
    color: white;
}

.color-option.selected {
    border-color: var(--sm-text);
    box-shadow: 0 0 0 3px var(--sm-primary-soft);
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

@media (max-width: 992px) {

    .page-header,
    .toolbar {
        flex-direction: column;
        align-items: flex-start;
    }

    .filter-area {
        width: 100%;
        flex-direction: column;
    }

    .search-box,
    .semester-select {
        width: 100%;
    }
}
</style>