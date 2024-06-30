import axios from 'axios'

// const host = 'http://192.168.43.128:3308'
// const host = 'http://123.60.53.131:3308'
// const host = 'http://120.46.129.79:3308'
// const host = 'http://124.70.109.243:3308'
const host = 'http://127.0.0.1:3308'

// const host1 = 'http://59f7b8ba.r10.vip.cpolar.cn'

export function get(url: string): Promise<any> {
  return new Promise((resolve, reject) => {
    axios
      .get(`${host}${url}`, {
        timeout: 5000,
        headers: {
          token: window.localStorage.getItem('xxqToken')
        }
      })
      .then((res) => {
        if (res.data.code != 200) {
          reject(res.data.msg)
        } else {
          resolve(res)
        }
      })
      .catch((err) => {
        reject(err)
      })
  })
}

export function post(url: string, data: any, withToken: boolean): Promise<any> {
  const options = withToken
    ? {
        timeout: 5000,
        headers: {
          token: window.localStorage.getItem('xxqToken')
        }
      }
    : {
        timeout: 5000
      }
  return new Promise((resolve, reject) => {
    axios
      .post(`${host}${url}`, data, options)
      .then((res) => {
        if (res.data.code != 200) {
          reject(res.data.msg)
        } else {
          resolve(res)
        }
      })
      .catch((err) => {
        reject(err)
      })
  })
}
