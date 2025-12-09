<template>
  <div style="padding: 20px;">
    <h1>API 测试工具</h1>
    
    <!-- 请求配置 -->
    <div style="margin-bottom: 20px;">
      <div style="margin-bottom: 10px;">
        <label>请求方法：</label>
        <select v-model="method">
          <option>GET</option>
          <option>POST</option>
          <option>PUT</option>
          <option>DELETE</option>
          <option>PATCH</option>
        </select>
      </div>
      
      <div style="margin-bottom: 10px;">
        <label>请求URL：</label>
        <input v-model="url" type="text" style="width: 500px;" placeholder="https://api.example.com/endpoint">
      </div>
    </div>

    <!-- Headers 表格 -->
    <div style="margin-bottom: 20px;">
      <h3>Headers <button @click="addHeader">+</button></h3>
      <table border="1" cellpadding="5" style="border-collapse: collapse;">
        <thead>
          <tr>
            <th>启用</th>
            <th>Key</th>
            <th>Value</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(header, index) in headers" :key="index">
            <td><input type="checkbox" v-model="header.enabled"></td>
            <td><input v-model="header.key" type="text" style="width: 200px;"></td>
            <td><input v-model="header.value" type="text" style="width: 300px;"></td>
            <td><button @click="removeHeader(index)">删除</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Query Params 表格 -->
    <div style="margin-bottom: 20px;">
      <h3>Query Params <button @click="addParam">+</button></h3>
      <table border="1" cellpadding="5" style="border-collapse: collapse;">
        <thead>
          <tr>
            <th>启用</th>
            <th>Key</th>
            <th>Value</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(param, index) in params" :key="index">
            <td><input type="checkbox" v-model="param.enabled"></td>
            <td><input v-model="param.key" type="text" style="width: 200px;"></td>
            <td><input v-model="param.value" type="text" style="width: 300px;"></td>
            <td><button @click="removeParam(index)">删除</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Body -->
    <div style="margin-bottom: 20px;" v-if="['POST', 'PUT', 'PATCH'].includes(method)">
      <h3>Body</h3>
      <div style="margin-bottom: 10px;">
        <label>
          <input type="radio" v-model="bodyType" value="json"> JSON
        </label>
        <label style="margin-left: 10px;">
          <input type="radio" v-model="bodyType" value="form"> Form Data
        </label>
        <label style="margin-left: 10px;">
          <input type="radio" v-model="bodyType" value="raw"> Raw Text
        </label>
      </div>

      <!-- JSON Body -->
      <div v-if="bodyType === 'json'">
        <textarea v-model="bodyJson" style="width: 600px; height: 150px;" placeholder='{"key": "value"}'></textarea>
      </div>

      <!-- Form Data -->
      <div v-if="bodyType === 'form'">
        <button @click="addFormData" style="margin-bottom: 10px;">+</button>
        <table border="1" cellpadding="5" style="border-collapse: collapse;">
          <thead>
            <tr>
              <th>启用</th>
              <th>Key</th>
              <th>Value</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in formData" :key="index">
              <td><input type="checkbox" v-model="item.enabled"></td>
              <td><input v-model="item.key" type="text" style="width: 200px;"></td>
              <td><input v-model="item.value" type="text" style="width: 300px;"></td>
              <td><button @click="removeFormData(index)">删除</button></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Raw Text -->
      <div v-if="bodyType === 'raw'">
        <textarea v-model="bodyRaw" style="width: 600px; height: 150px;"></textarea>
      </div>
    </div>

    <!-- 发送按钮 -->
    <div style="margin-bottom: 20px;">
      <button @click="sendRequest" style="padding: 10px 30px; font-size: 16px;">发送请求</button>
      <button @click="clearAll" style="padding: 10px 30px; font-size: 16px; margin-left: 10px;">清空</button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" style="margin-bottom: 20px;">
      <p>请求中...</p>
    </div>

    <!-- 响应结果 -->
    <div v-if="response">
      <h3>响应结果</h3>
      <div style="margin-bottom: 10px;">
        <strong>状态码：</strong> 
        <span :style="{color: response.status >= 200 && response.status < 300 ? 'green' : 'red'}">
          {{ response.status }} {{ response.statusText }}
        </span>
      </div>
      <div style="margin-bottom: 10px;">
        <strong>耗时：</strong> {{ response.duration }}ms
      </div>
      
      <h4>响应头：</h4>
      <pre style="background: #f5f5f5; padding: 10px; overflow: auto;">{{ response.headers }}</pre>
      
      <h4>响应体：</h4>
      <pre style="background: #f5f5f5; padding: 10px; overflow: auto; max-height: 400px;">{{ response.data }}</pre>
    </div>

    <!-- 错误信息 -->
    <div v-if="error" style="color: red; margin-top: 20px;">
      <h3>错误信息</h3>
      <pre>{{ error }}</pre>
    </div>

    <!-- 历史记录 -->
    <div v-if="history.length > 0" style="margin-top: 30px;">
      <h3>请求历史 <button @click="clearHistory">清空历史</button></h3>
      <div v-for="(item, index) in history" :key="index" 
           style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; cursor: pointer;"
           @click="loadHistory(item)">
        <strong>{{ item.method }}</strong> {{ item.url }} - 
        <span :style="{color: item.status >= 200 && item.status < 300 ? 'green' : 'red'}">
          {{ item.status }}
        </span>
        <span style="margin-left: 10px; color: #666; font-size: 12px;">{{ item.timestamp }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 请求配置
const method = ref('GET')
const url = ref('')

// Headers
const headers = ref([
  { enabled: true, key: 'Content-Type', value: 'application/json' }
])

// Query Params
const params = ref([
  { enabled: true, key: '', value: '' }
])

// Body
const bodyType = ref('json')
const bodyJson = ref('')
const bodyRaw = ref('')
const formData = ref([
  { enabled: true, key: '', value: '' }
])

// 响应
const loading = ref(false)
const response = ref(null)
const error = ref(null)

// 历史记录
const history = ref([])

// 添加/删除 Header
const addHeader = () => {
  headers.value.push({ enabled: true, key: '', value: '' })
}
const removeHeader = (index) => {
  headers.value.splice(index, 1)
}

// 添加/删除 Param
const addParam = () => {
  params.value.push({ enabled: true, key: '', value: '' })
}
const removeParam = (index) => {
  params.value.splice(index, 1)
}

// 添加/删除 FormData
const addFormData = () => {
  formData.value.push({ enabled: true, key: '', value: '' })
}
const removeFormData = (index) => {
  formData.value.splice(index, 1)
}

// 发送请求
const sendRequest = async () => {
  error.value = null
  response.value = null
  loading.value = true

  try {
    // 构建 URL
    let fullUrl = url.value
    const enabledParams = params.value.filter(p => p.enabled && p.key)
    if (enabledParams.length > 0) {
      const queryString = enabledParams
        .map(p => `${encodeURIComponent(p.key)}=${encodeURIComponent(p.value)}`)
        .join('&')
      fullUrl += (fullUrl.includes('?') ? '&' : '?') + queryString
    }

    // 构建 Headers
    const reqHeaders = {}
    headers.value
      .filter(h => h.enabled && h.key)
      .forEach(h => reqHeaders[h.key] = h.value)

    // 构建请求配置
    const config = {
      method: method.value,
      headers: reqHeaders
    }

    // 构建 Body
    if (['POST', 'PUT', 'PATCH'].includes(method.value)) {
      if (bodyType.value === 'json') {
        config.body = bodyJson.value
      } else if (bodyType.value === 'form') {
        const formDataObj = new URLSearchParams()
        formData.value
          .filter(f => f.enabled && f.key)
          .forEach(f => formDataObj.append(f.key, f.value))
        config.body = formDataObj
      } else if (bodyType.value === 'raw') {
        config.body = bodyRaw.value
      }
    }

    // 记录开始时间
    const startTime = Date.now()

    // 发送请求
    const res = await fetch(fullUrl, config)
    const duration = Date.now() - startTime

    // 获取响应头
    const resHeaders = {}
    res.headers.forEach((value, key) => {
      resHeaders[key] = value
    })

    // 获取响应体
    let data
    const contentType = res.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      data = await res.json()
      data = JSON.stringify(data, null, 2)
    } else {
      data = await res.text()
    }

    response.value = {
      status: res.status,
      statusText: res.statusText,
      headers: JSON.stringify(resHeaders, null, 2),
      data: data,
      duration: duration
    }

    // 保存到历史
    history.value.unshift({
      method: method.value,
      url: fullUrl,
      status: res.status,
      timestamp: new Date().toLocaleString(),
      config: JSON.parse(JSON.stringify({
        method: method.value,
        url: url.value,
        headers: headers.value,
        params: params.value,
        bodyType: bodyType.value,
        bodyJson: bodyJson.value,
        bodyRaw: bodyRaw.value,
        formData: formData.value
      }))
    })

  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// 清空所有
const clearAll = () => {
  url.value = ''
  headers.value = [{ enabled: true, key: 'Content-Type', value: 'application/json' }]
  params.value = [{ enabled: true, key: '', value: '' }]
  formData.value = [{ enabled: true, key: '', value: '' }]
  bodyJson.value = ''
  bodyRaw.value = ''
  response.value = null
  error.value = null
}

// 清空历史
const clearHistory = () => {
  history.value = []
}

// 加载历史记录
const loadHistory = (item) => {
  const config = item.config
  method.value = config.method
  url.value = config.url
  headers.value = config.headers
  params.value = config.params
  bodyType.value = config.bodyType
  bodyJson.value = config.bodyJson
  bodyRaw.value = config.bodyRaw
  formData.value = config.formData
}
</script>