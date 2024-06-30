import axios from 'axios'

// 创建一个axios实例
const apiClient = axios.create({
  baseURL: 'http://59f7b8ba.r10.vip.cpolar.cn', // 替换为你的后端API地址
  withCredentials: false, // 如果你需要发送跨域请求并携带cookie，将其设置为true
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json'
  }
});

// export async function askQuestion(data) {
//   return await apiClient.post('/chat', data);
// }

export async function askQuestion(data) {
  return await apiClient.post('/chat', data)
}
