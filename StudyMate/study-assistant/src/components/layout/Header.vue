<template>
    <header ref="headerRef" class="header">
        <div class="left-header">
            <button class="mobile-menu-btn" @click="emit('toggle-sidebar')">
                <i class="bi bi-list"></i>
            </button>
            <!-- Page Info -->
            <div class="page-info">
                <h5>{{ currentPage.title }}</h5>
                <p>{{ currentPage.description }}</p>
            </div>
        </div>


        <!-- Actions -->
        <div class="header-actions">
            <!-- Search -->
            <div class="search-wrapper">
                <div class="search-box" :class="{ active: searchKeyword }">
                    <i class="bi bi-search"></i>

                    <input v-model="searchKeyword" type="text" placeholder="Tìm trang chức năng..."
                        @focus="showSearchResults = true" @keydown.enter="goToFirstResult" />

                    <button v-if="searchKeyword" class="clear-btn" @click="clearSearch">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>

                <div v-if="showSearchResults && searchKeyword && filteredPages.length > 0" class="search-results">
                    <button v-for="page in filteredPages" :key="page.path" class="search-result-item"
                        @click="goToPage(page.path)">
                        <div class="result-icon">
                            <i :class="page.icon"></i>
                        </div>

                        <div>
                            <strong>{{ page.title }}</strong>
                            <small>{{ page.description }}</small>
                        </div>
                    </button>
                </div>

                <div v-if="showSearchResults && searchKeyword && filteredPages.length === 0"
                    class="search-results empty-result">
                    Không tìm thấy trang phù hợp.
                </div>
            </div>

            <!-- Notification -->
            <div class="notification-wrapper">
                <button class="icon-btn" @click="toggleNotifications">
                    <i class="bi bi-bell"></i>

                    <span v-if="pendingReminders > 0" class="notification-count">
                        {{ pendingReminders > 9 ? '9+' : pendingReminders }}
                    </span>
                </button>

                <div v-if="showNotifications" class="notification-dropdown">
                    <div class="dropdown-header">
                        <div>
                            <h5>Thông báo</h5>
                            <p>{{ pendingReminders }} nhắc nhở đang chờ gửi</p>
                        </div>

                        <RouterLink to="/nhac-nho-email" @click="showNotifications = false">
                            Xem tất cả
                        </RouterLink>
                    </div>

                    <div v-if="displayReminders.length === 0" class="notification-empty">
                        <div>
                            <i class="bi bi-bell-slash"></i>
                        </div>
                        <p>Chưa có thông báo mới.</p>
                    </div>

                    <div v-else class="notification-list">
                        <div v-for="reminder in displayReminders" :key="reminder.id" class="notification-item"
                            :class="{ due: isDue(reminder) }">
                            <div class="notification-icon" :class="reminder.targetType.toLowerCase()">
                                <i :class="reminder.targetType === 'TASK'
                                    ? 'bi bi-check2-square'
                                    : 'bi bi-calendar-event'
                                    "></i>
                            </div>

                            <div class="notification-content">
                                <strong>{{ getReminderTitle(reminder) }}</strong>
                                <p>
                                    {{ reminder.targetType === 'TASK' ? 'Bài tập' : 'Lịch thi' }}
                                    · {{ formatDateTime(reminder.remindAt) }}
                                </p>

                                <span v-if="isDue(reminder)" class="due-text">
                                    Đã đến thời gian gửi email
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- User -->
            <div class="user-wrapper">
                <button class="user-btn" @click="toggleUserMenu">
                    <div class="avatar">{{ userInitial }}</div>

                    <div class="user-text">
                        <strong>{{ shortUserName }}</strong>
                        <span>{{ currentUser.role }}</span>
                    </div>

                    <i class="bi bi-chevron-down arrow"></i>
                </button>

                <div v-if="showUserMenu" class="user-dropdown">
                    <div class="user-dropdown-header">
                        <div class="avatar large">{{ userInitial }}</div>
                        <div>
                            <strong>{{ currentUser.fullName }}</strong>
                            <p>{{ currentUser.email }}</p>
                        </div>
                    </div>

                    <RouterLink to="/dashboard" class="dropdown-link" @click="showUserMenu = false">
                        <i class="bi bi-grid-1x2"></i>
                        Dashboard
                    </RouterLink>

                    <RouterLink to="/nhac-nho-email" class="dropdown-link" @click="showUserMenu = false">
                        <i class="bi bi-bell"></i>
                        Cài đặt nhắc nhở
                    </RouterLink>

                    <button class="dropdown-link logout-link" @click="logout">
                        <i class="bi bi-box-arrow-right"></i>
                        Đăng xuất
                    </button>
                </div>
            </div>
        </div>
    </header>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { authStore } from '../../stores/auth'

const router = useRouter()
const route = useRoute()

const emit = defineEmits(['toggle-sidebar'])

const headerRef = ref(null)
const searchKeyword = ref('')
const showSearchResults = ref(false)
const showNotifications = ref(false)
const showUserMenu = ref(false)
const reminders = ref([])
const tasks = ref([])
const exams = ref([])

const pages = [
    {
        path: '/dashboard',
        title: 'Dashboard',
        description: 'Tổng quan học tập',
        icon: 'bi bi-grid-1x2-fill',
    },
    {
        path: '/mon-hoc',
        title: 'Môn học',
        description: 'Theo dõi danh sách môn học',
        icon: 'bi bi-book-fill',
    },
    {
        path: '/bai-tap',
        title: 'Bài tập',
        description: 'Quản lý deadline bài tập',
        icon: 'bi bi-check2-square',
    },
    {
        path: '/lich-thi',
        title: 'Lịch thi',
        description: 'Theo dõi kỳ thi sắp tới',
        icon: 'bi bi-calendar-event',
    },
    {
        path: '/ke-hoach-on-tap',
        title: 'Kế hoạch ôn tập',
        description: 'Lập lịch học theo ngày',
        icon: 'bi bi-calendar-check',
    },
    {
        path: '/tai-lieu',
        title: 'Tài liệu học tập',
        description: 'Lưu dữ liệu cho chatbot',
        icon: 'bi bi-file-earmark-text-fill',
    },
    {
        path: '/chatbot',
        title: 'Chatbot hỏi đáp',
        description: 'Hỏi bài với StudyMate AI',
        icon: 'bi bi-robot',
    },
    {
        path: '/nhac-nho-email',
        title: 'Nhắc nhở Email',
        description: 'Thiết lập thông báo deadline',
        icon: 'bi bi-bell-fill',
    },
]

const pageDescriptions = {
    '/dashboard': {
        title: 'Tổng quan học tập',
        description: 'Theo dõi tiến độ và học tập hiệu quả hơn',
    },
    '/mon-hoc': {
        title: 'Môn học',
        description: 'Quản lý các môn học trong học kỳ',
    },
    '/bai-tap': {
        title: 'Bài tập & Deadline',
        description: 'Theo dõi công việc cần hoàn thành',
    },
    '/lich-thi': {
        title: 'Lịch thi',
        description: 'Chuẩn bị tốt cho các kỳ thi sắp tới',
    },
    '/ke-hoach-on-tap': {
        title: 'Kế hoạch ôn tập',
        description: 'Sắp xếp lịch học theo ngày',
    },
    '/tai-lieu': {
        title: 'Tài liệu học tập',
        description: 'Lưu nội dung để chatbot hỗ trợ chính xác hơn',
    },
    '/chatbot': {
        title: 'Chatbot hỏi đáp',
        description: 'Hỏi bài dựa trên tài liệu cá nhân',
    },
    '/nhac-nho-email': {
        title: 'Nhắc nhở Email',
        description: 'Không bỏ lỡ deadline và lịch thi quan trọng',
    },
}

const currentUser = computed(() => {
    const user = authStore.state.user

    return {
        fullName: user?.full_name || 'Sinh viên',
        email: user?.email || '',
        role: user?.role || 'Sinh viên',
    }
})

const currentPage = computed(() => {
    return (
        pageDescriptions[route.path] || {
            title: 'StudyMate',
            description: 'Trợ lý học tập cá nhân',
        }
    )
})

const userInitial = computed(() => {
    const parts = currentUser.value.fullName.trim().split(' ')
    return parts[parts.length - 1].charAt(0).toUpperCase()
})

const shortUserName = computed(() => {
    const parts = currentUser.value.fullName.trim().split(' ')
    return parts.slice(-2).join(' ')
})

const filteredPages = computed(() => {
    const keyword = searchKeyword.value.trim().toLowerCase()

    if (!keyword) {
        return []
    }

    return pages.filter(
        (page) =>
            page.title.toLowerCase().includes(keyword) ||
            page.description.toLowerCase().includes(keyword),
    )
})

const pendingReminders = computed(() => {
    return reminders.value.filter((reminder) => reminder.status === 'PENDING').length
})

const displayReminders = computed(() => {
    return [...reminders.value]
        .filter((reminder) => reminder.status === 'PENDING')
        .sort(
            (first, second) =>
                new Date(first.remindAt).getTime() -
                new Date(second.remindAt).getTime(),
        )
        .slice(0, 4)
})

const loadNotificationData = () => {
    reminders.value = []
    tasks.value = []
    exams.value = []
}

const getReminderTitle = (reminder) => {
    if (reminder.targetType === 'TASK') {
        const task = tasks.value.find(
            (item) => String(item.id) === String(reminder.taskId),
        )

        return task?.title || 'Bài tập cần hoàn thành'
    }

    const exam = exams.value.find(
        (item) => String(item.id) === String(reminder.examId),
    )

    return exam?.title || 'Kỳ thi sắp tới'
}

const formatDateTime = (value) => {
    if (!value) {
        return 'Chưa xác định'
    }

    return new Date(value).toLocaleString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit',
        day: '2-digit',
        month: '2-digit',
    })
}

const isDue = (reminder) => {
    return new Date(reminder.remindAt).getTime() <= Date.now()
}

const clearSearch = () => {
    searchKeyword.value = ''
    showSearchResults.value = false
}

const goToPage = (path) => {
    clearSearch()
    router.push(path)
}

const goToFirstResult = () => {
    if (filteredPages.value.length > 0) {
        goToPage(filteredPages.value[0].path)
    }
}

const toggleNotifications = () => {
    loadNotificationData()
    showNotifications.value = !showNotifications.value
    showUserMenu.value = false
    showSearchResults.value = false
}

const toggleUserMenu = () => {
    showUserMenu.value = !showUserMenu.value
    showNotifications.value = false
    showSearchResults.value = false
}

const logout = async () => {
    await authStore.logout()

    showUserMenu.value = false
    router.push('/dang-nhap')
}

const handleClickOutside = (event) => {
    if (headerRef.value && !headerRef.value.contains(event.target)) {
        showNotifications.value = false
        showUserMenu.value = false
        showSearchResults.value = false
    }
}

watch(
    () => route.path,
    () => {
        showNotifications.value = false
        showUserMenu.value = false
        showSearchResults.value = false
        searchKeyword.value = ''
        loadNotificationData()
    },
)

onMounted(() => {
    loadNotificationData()
    document.addEventListener('click', handleClickOutside)
    window.addEventListener('focus', loadNotificationData)
    window.addEventListener('storage', loadNotificationData)
})

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
    window.removeEventListener('focus', loadNotificationData)
    window.removeEventListener('storage', loadNotificationData)
})
</script>

<style scoped>
.header {
    position: sticky;
    top: 0;
    z-index: 100;
    height: 78px;
    padding: 0 28px;
    border-bottom: 1px solid var(--sm-border);
    background: rgba(255, 253, 250, 0.92);
    backdrop-filter: blur(16px);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.left-header {
    display: flex;
    align-items: center;
    gap: 13px;
}

.page-info h5 {
    margin: 0 0 4px;
    color: var(--sm-text);
    font-size: 17px;
    font-weight: 700;
}

.page-info p {
    margin: 0;
    color: var(--sm-text-soft);
    font-size: 13px;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
}

.mobile-menu-btn {
    display: none;
    width: 43px;
    height: 43px;
    border: 1px solid var(--sm-border);
    border-radius: 12px;
    color: var(--sm-text);
    background: var(--sm-accent-soft);
    font-size: 24px;
}

.mobile-menu-btn:hover {
    color: var(--sm-primary-dark);
    background: var(--sm-primary-soft);
}

.search-wrapper,
.notification-wrapper,
.user-wrapper {
    position: relative;
}

.search-box {
    width: 270px;
    height: 45px;
    padding: 0 13px;
    border: 1px solid transparent;
    border-radius: 13px;
    color: var(--sm-text-soft);
    background: #f5eee5;
    display: flex;
    align-items: center;
    gap: 9px;
    transition: all 0.2s ease;
}

.search-box i {
    color: #9e8872;
}

.search-box:focus-within,
.search-box.active {
    border-color: #d8b992;
    background: #fffdfa;
    box-shadow: 0 0 0 3px #f4e7d7;
}

.search-box input {
    flex: 1;
    border: none;
    outline: none;
    color: var(--sm-text);
    background: transparent;
}

.search-box input::placeholder {
    color: #a09083;
}

.clear-btn {
    border: none;
    color: #a09083;
    background: transparent;
}

.search-results {
    position: absolute;
    top: 54px;
    left: 0;
    width: 320px;
    padding: 8px;
    border: 1px solid var(--sm-border);
    border-radius: 15px;
    background: var(--sm-card);
    box-shadow: var(--sm-shadow-md);
}

.search-result-item {
    width: 100%;
    padding: 10px;
    border: none;
    border-radius: 10px;
    background: transparent;
    display: flex;
    align-items: center;
    gap: 11px;
    text-align: left;
}

.search-result-item:hover {
    background: var(--sm-accent-soft);
}

.result-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    color: var(--sm-primary);
    background: var(--sm-primary-soft);
    display: flex;
    align-items: center;
    justify-content: center;
}

.search-result-item strong {
    display: block;
    color: var(--sm-text);
    font-size: 13px;
}

.search-result-item small {
    color: var(--sm-text-soft);
    font-size: 11px;
}

.empty-result {
    padding: 18px;
    color: var(--sm-text-soft);
    font-size: 13px;
    text-align: center;
}

.icon-btn {
    position: relative;
    width: 45px;
    height: 45px;
    border: 1px solid var(--sm-border);
    border-radius: 13px;
    color: var(--sm-text);
    background: var(--sm-accent-soft);
    font-size: 20px;
}

.icon-btn:hover {
    color: var(--sm-primary-dark);
    background: var(--sm-primary-soft);
}

.notification-count {
    position: absolute;
    top: -4px;
    right: -3px;
    min-width: 19px;
    height: 19px;
    padding: 0 5px;
    border: 2px solid var(--sm-card);
    border-radius: 20px;
    color: white;
    background: var(--sm-danger);
    font-size: 10px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}

.notification-dropdown {
    position: absolute;
    top: 56px;
    right: 0;
    width: 370px;
    padding: 17px;
    border: 1px solid var(--sm-border);
    border-radius: 17px;
    background: var(--sm-card);
    box-shadow: var(--sm-shadow-md);
}

.dropdown-header {
    margin-bottom: 14px;
    padding-bottom: 13px;
    border-bottom: 1px solid var(--sm-border);
    display: flex;
    justify-content: space-between;
}

.dropdown-header h5 {
    margin: 0 0 4px;
    color: var(--sm-text);
    font-size: 15px;
    font-weight: 700;
}

.dropdown-header p {
    margin: 0;
    color: var(--sm-text-soft);
    font-size: 12px;
}

.dropdown-header a {
    color: var(--sm-primary);
    text-decoration: none;
    font-size: 12px;
    font-weight: 600;
}

.dropdown-header a:hover {
    color: var(--sm-primary-dark);
}

.notification-empty {
    padding: 30px 10px;
    text-align: center;
}

.notification-empty div {
    width: 51px;
    height: 51px;
    margin: 0 auto 11px;
    border-radius: 50%;
    color: var(--sm-primary);
    background: var(--sm-primary-soft);
    font-size: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.notification-empty p {
    margin: 0;
    color: var(--sm-text-soft);
    font-size: 13px;
}

.notification-list {
    display: flex;
    flex-direction: column;
    gap: 9px;
}

.notification-item {
    padding: 11px;
    border-radius: 12px;
    background: var(--sm-accent-soft);
    display: flex;
    gap: 10px;
}

.notification-item.due {
    background: var(--sm-danger-bg);
}

.notification-icon {
    width: 40px;
    height: 40px;
    flex-shrink: 0;
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.notification-icon.task {
    color: var(--sm-primary);
    background: var(--sm-primary-soft);
}

.notification-icon.exam {
    color: var(--sm-warning);
    background: var(--sm-warning-bg);
}

.notification-content strong {
    color: var(--sm-text);
    font-size: 13px;
}

.notification-content p {
    margin: 4px 0 0;
    color: var(--sm-text-soft);
    font-size: 11px;
}

.due-text {
    display: block;
    margin-top: 5px;
    color: var(--sm-danger);
    font-size: 11px;
    font-weight: 600;
}

.user-btn {
    height: 49px;
    padding: 5px 9px 5px 6px;
    border: 1px solid var(--sm-border);
    border-radius: 14px;
    background: var(--sm-card);
    display: flex;
    align-items: center;
    gap: 9px;
}

.user-btn:hover {
    border-color: var(--sm-border-strong);
    box-shadow: var(--sm-shadow-sm);
}

.avatar {
    width: 38px;
    height: 38px;
    border-radius: 11px;
    color: var(--sm-primary-dark);
    background: var(--sm-primary-soft);
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
}

.user-text {
    min-width: 83px;
    text-align: left;
}

.user-text strong {
    display: block;
    color: var(--sm-text);
    font-size: 13px;
}

.user-text span {
    color: var(--sm-text-soft);
    font-size: 11px;
}

.arrow {
    color: #a09083;
    font-size: 11px;
}

.user-dropdown {
    position: absolute;
    top: 58px;
    right: 0;
    width: 280px;
    padding: 10px;
    border: 1px solid var(--sm-border);
    border-radius: 16px;
    background: var(--sm-card);
    box-shadow: var(--sm-shadow-md);
}

.user-dropdown-header {
    padding: 9px 9px 14px;
    margin-bottom: 7px;
    border-bottom: 1px solid var(--sm-border);
    display: flex;
    align-items: center;
    gap: 10px;
}

.avatar.large {
    width: 44px;
    height: 44px;
}

.user-dropdown-header strong {
    display: block;
    color: var(--sm-text);
    font-size: 13px;
}

.user-dropdown-header p {
    max-width: 182px;
    margin: 4px 0 0;
    overflow: hidden;
    color: var(--sm-text-soft);
    font-size: 11px;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.dropdown-link {
    width: 100%;
    height: 43px;
    padding: 0 11px;
    border: none;
    border-radius: 10px;
    color: var(--sm-text);
    background: transparent;
    text-decoration: none;
    font-size: 13px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 10px;
}

.dropdown-link:hover {
    color: var(--sm-primary-dark);
    background: var(--sm-primary-soft);
}

.logout-link:hover {
    color: var(--sm-danger);
    background: var(--sm-danger-bg);
}

@media (max-width: 1000px) {
    .mobile-menu-btn {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .page-info p,
    .user-text,
    .arrow {
        display: none;
    }

    .search-box {
        width: 210px;
    }
}

@media (max-width: 700px) {
    .header {
        padding: 0 16px;
    }

    .page-info {
        display: none;
    }

    .search-box {
        width: 170px;
    }

    .notification-dropdown {
        right: -50px;
        width: min(370px, calc(100vw - 32px));
    }
}
</style>