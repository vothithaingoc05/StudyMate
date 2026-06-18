<template>
    <div class="app-layout">
        <Sidebar :is-open="sidebarOpen" @close="closeSidebar" />

        <div v-if="sidebarOpen" class="sidebar-overlay" @click="closeSidebar"></div>

        <div class="main-wrapper">
            <Header @toggle-sidebar="toggleSidebar" />

            <main class="content-area">
                <RouterView />
            </main>
        </div>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import Sidebar from '../components/layout/Sidebar.vue'
import Header from '../components/layout/Header.vue'

const route = useRoute()
const sidebarOpen = ref(false)

const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
    sidebarOpen.value = false
}

watch(
    () => route.path,
    () => {
        closeSidebar()
    },
)
</script>

<style scoped>
.app-layout {
    min-height: 100vh;
    display: flex;
    background:
        radial-gradient(circle at 96% 6%, rgba(217, 174, 118, 0.12), transparent 24%),
        var(--sm-bg);
}

.main-wrapper {
    width: calc(100% - 265px);
    margin-left: 265px;
    min-height: 100vh;
}

.content-area {
    min-height: calc(100vh - 78px);
    padding: 28px;
}

.sidebar-overlay {
    display: none;
}

@media (max-width: 900px) {
    .main-wrapper {
        width: 100%;
        margin-left: 0;
    }

    .content-area {
        padding: 18px;
    }

    .sidebar-overlay {
        position: fixed;
        inset: 0;
        z-index: 190;
        display: block;
        background: rgba(46, 35, 28, 0.54);
        backdrop-filter: blur(2px);
    }
}

@media (max-width: 576px) {
    .content-area {
        padding: 14px;
    }
}
</style>