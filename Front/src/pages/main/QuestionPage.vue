<script setup>
import { ref, onMounted } from 'vue'
import { askQuestion } from '@/lib/axios/ask'
import LocalCache from '@/utils/cache'
import BgParticle from '../../components/BgParticle.vue'

// 假设已经有用户登录信息
const currentUser = LocalCache.getCache('currentUser') || 'guest'

const question = ref('')
const answer = ref('')
const conversations = ref([]) // 存储不同的会话
const selectedConversationIndex = ref(null) // 选择的会话索引
const selectedImage = ref(null) // 存储选择的图片
const imageBase64 = ref('') // 存储图片的base64编码

// 页面加载时从 LocalStorage 中加载历史记录
onMounted(() => {
  const storedConversations = LocalCache.getCache(`conversations_${currentUser}`)
  if (storedConversations) {
    conversations.value = storedConversations
  }
})

function submitQuestion() {
  if (question.value.trim() === '') {
    answer.value = '请输入您的问题'
    return
  }

  // 构建历史信息
  const historyData = selectedConversationIndex.value !== null ? conversations.value[selectedConversationIndex.value].map(([q, a]) => [q, a]) : []

  // 构建请求数据
  const data = {
    history: historyData,
    query: question.value,
    image: imageBase64.value
  }

  askQuestion(data)
    .then(response => {
      console.log(response)
      const newAnswer = response.data.response
      // 保存到历史记录
      if (selectedConversationIndex.value !== null) {
        conversations.value[selectedConversationIndex.value].push([question.value, newAnswer, imageBase64.value])
      } else {
        conversations.value.push([[question.value, newAnswer, imageBase64.value]])
        selectedConversationIndex.value = conversations.value.length - 1
      }
      // 更新当前答案
      answer.value = newAnswer
      // 清空问题输入框
      question.value = ''
      // 清空图片
      selectedImage.value = null
      imageBase64.value = ''
      // 存储在 LocalStorage
      LocalCache.setCache(`conversations_${currentUser}`, conversations.value)
    })
    .catch(err => {
      answer.value = '抱歉，无法获取答案，请稍后再试'
      console.log(err)
    })
}

// 处理图片上传
function handleImageUpload(event) {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = () => {
      // 移除data:image/png;base64,前缀
      const base64Data = reader.result.split(',')[1]
      imageBase64.value = base64Data
      selectedImage.value = reader.result // 用于预览
    }
    reader.readAsDataURL(file)
  }
}

function selectConversation(index) {
  selectedConversationIndex.value = index
}

function createNewConversation() {
  conversations.value.push([])
  selectedConversationIndex.value = conversations.value.length - 1
}

function deleteConversation(index) {
  conversations.value.splice(index, 1)
  if (selectedConversationIndex.value === index) {
    selectedConversationIndex.value = null
  } else if (selectedConversationIndex.value > index) {
    selectedConversationIndex.value--
  }
  // 更新LocalStorage
  LocalCache.setCache(`conversations_${currentUser}`, conversations.value)
}

function handleKeyPress(event) {
  if (event.key === 'Enter') {
    submitQuestion()
  }
}
</script>

<template>
  <v-row style="margin-top: 20px;">
    <v-col cols="12" md="1"></v-col>
    <!-- 左侧会话历史 -->
    <v-col cols="12" md="2" class="leftHistory">
      <v-card>
        <v-card-title class="headline">会话历史</v-card-title>
        <v-btn color="primary" block @click="createNewConversation">新建会话</v-btn>
        <v-card-text>
          <v-list dense>
            <v-list-item-group v-model="selectedConversationIndex" active-class="v-list-item--active">
              <v-list-item v-for="(conversation, index) in conversations" :key="index" @click="selectConversation(index)">
                <v-list-item-content class="d-flex justify-space-between align-center">
                  <div>
                    <v-list-item-title>会话 {{ index + 1 }}</v-list-item-title>
                    <v-list-item-subtitle>{{ conversation[0] ? conversation[0][0] : '新会话' }}</v-list-item-subtitle>
                  </div>
                  <v-btn icon small @click.stop="deleteConversation(index)">
                    <v-icon small>mdi-delete</v-icon>
                  </v-btn>
                </v-list-item-content>
              </v-list-item>
            </v-list-item-group>
          </v-list>
        </v-card-text>
      </v-card>
    </v-col>
    <!-- 右侧问答部分 -->
    <v-col cols="12" md="8" class="rightAsk">
      <v-card class="d-flex flex-column" style="height: 80vh;">
        <v-card-title class="headline">交通问答</v-card-title>
        <v-card-text class="flex-grow-1" style="overflow-y: auto; height: 80vh">
          <v-row>
            <v-col>
              <div v-if="selectedConversationIndex !== null">
                <div v-for="(item, index) in conversations[selectedConversationIndex]" :key="index">
                  <p><strong>{{ currentUser }}：</strong> {{ item[0] }}</p>
                  <p><strong>TransGPT：</strong> {{ item[1] }}</p>
                  <div v-if="item[2]">
                    <img :src="'data:image/png;base64,' + item[2]" alt="Uploaded Image" style="max-width: 100%;" />
                  </div>
                  <hr />
                </div>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-text style="position: sticky; bottom: 0; background: white;">
          <v-row>
            <v-col style="padding-bottom: 0">
              <v-btn outlined @click="$refs.fileInput.click()">选择文件</v-btn>
              <input ref="fileInput" type="file" @change="handleImageUpload" style="display: none;" />
              <v-text-field
                v-model="question"
                label="请输入您的问题"
                outlined
                clearable
                @keypress="handleKeyPress"
              >
                <template #append>
                  <v-btn icon @click="submitQuestion">
                    <v-icon>mdi-send</v-icon>
                  </v-btn>
                </template>
              </v-text-field>
            </v-col>
          </v-row>
          <!-- 图片预览 -->
          <v-row v-if="selectedImage">
            <v-col>
              <img :src="selectedImage" alt="Selected Image" style="max-width: 100%;" />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
  <BgParticle />
</template>

<style scoped>
.v-list-item--active {
  background-color: #e0e0e0 !important;
}
</style>
