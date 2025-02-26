import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/pages/LoginPage.vue'
import AboutPage from '@/pages/AboutPage.vue'
import TestPage from '@/pages/TestPage.vue'
import MainPage from '@/pages/MainPage.vue'

import HomePage from '@/pages/main/HomePage.vue'
import CountPage from '@/pages/main/CountPage.vue'
import AdminPage from '@/pages/main/AdminPage.vue'
import WarningPage from '@/pages/main/WarningPage.vue'
import QuestionPage from '@/pages/main/QuestionPage.vue'
import DoubleSubwayPage from '@/pages/main/DoubleSubwayPage.vue'
import SingleSubwayPage from '@/pages/main/SingleSubwayPage.vue'
import { useTokenStore } from '@/stores/token'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      meta: {
        requireAuth: true
      },
      component: MainPage,
      children: [
        {
          path: '',
          name: 'home',
          meta: {
            requireAuth: true
          },
          component: HomePage,
        },
        {
          path: '/admin',
          name: 'admin',
          component: AdminPage,
          meta: {
            requireAuth: true
          },
        },
        {
          path: '/count',
          name: 'count',
          component: CountPage,
          meta: {
            requireAuth: true
          },
        },
        {
          path: '/warning',
          name: 'warning',
          component: WarningPage,
          meta: {
            requireAuth: true
          },
        },
        // 问答页面路由
        {
          path: '/question',
          name: 'question',
          component: QuestionPage,
          meta: {
            requireAuth: true
          },
        },
        // 单边地铁页面路由
        {
          path: '/singleSubway',
          name: 'singleSubway',
          component: SingleSubwayPage,
        }, 
        // 双边地铁页面路由
        {
          path: '/doubleSubway',
          name: 'doubleSubway',
          component: DoubleSubwayPage,
        }, 
      ]
    },
    // test页面路由
    {
      path: '/test',
      name: 'test',
      component: TestPage,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginPage
    },
    {
      path: '/about',
      name: 'about',
      component: AboutPage
    },
    {
      path: '/heat',
      name: 'heat',
      meta: {
        requireAuth: true
      },
      component: () => import('../components/HeatMap.vue')
    },
    {
      path: '/test',
      name: 'test',
      meta: {
        requireAuth: true
      },
      component: TestPage
    }
  ]
})

router.beforeEach((to, from) => {
  const tokenStore = useTokenStore()
  if (to.meta.requireAuth && !tokenStore.isLoggedIn && !import.meta.env.DEV) {
    router.replace('/login')
    // 返回 false 以取消导航
    return false
  }
  return true
})

export default router