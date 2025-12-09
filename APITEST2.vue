<template>
  <div class="api-tester">
    <h1>{{ message }}</h1>
    
    <!-- 请求配置区 -->
    <div class="request-section">
      <div class="request-line">
        <select v-model="requestMethod" class="method-select">
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
          <option value="DELETE">DELETE</option>
          <option value="PATCH">PATCH</option>
        </select>
        
        <input 
          v-model="apiUrl" 
          type="text" 
          placeholder="请输入API地址，例如: https://api.example.com/users"
          class="url-input"
        />
        
        <button @click="sendRequest" class="send-btn">发送请求</button>
      </div>
    </div>

    <!-- 标签页切换 -->
    <div class="tabs">
      <button 
        :class="['tab', { active: activeTab === 'params' }]"
        @click="activeTab = 'params'"
      >
        Query 参数
      </button>
      <button 
        :class="['tab', { active: activeTab === 'headers' }]"
        @click="activeTab = 'headers'"
      >
        请求头
      </button>
      <button 
        :class="['tab', { active: activeTab === 'body' }]"
        @click="activeTab = 'body'"
      >
        请求体
      </button>
    </div>

    <!-- Query 参数表格 -->
    <div v-show="activeTab === 'params'" class="table-container">
      <table class="param-table">
        <thead>
          <tr>
            <th width="40">启用</th>
            <th>键 (Key)</th>
            <th>值 (Value)</th>
            <th width="60">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(param, index) in queryParams" :key="index">
            <td>
              <input type="checkbox" v-model="param.enabled" />
            </td>
            <td>
              <input 
                v-model="param.key" 
                type="text" 
                placeholder="参数名"
                class="table-input"
              />
            </td>
            <td>
              <input 
                v-model="param.value" 
                type="text" 
                placeholder="参数值"
                class="table-input"
              />
            </td>
            <td>
              <button @click="removeParam(index)" class="btn-remove">-</button>
            </td>
          </tr>
        </tbody>
      </table>
      <button @click="addParam" class="btn-add">+ 添加参数</button>
    </div>

    <!-- 请求头表格 -->
    <div v-show="activeTab === 'headers'" class="table-container">
      <table class="param-table">
        <thead>
          <tr>
            <th width="40">启用</th>
            <th>键 (Key)</th>
            <th>值 (Value)</th>
            <th width="60">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(header, index) in headers" :key="index">
            <td>
              <input type="checkbox" v-model="header.enabled" />
            </td>
            <td>
              <input 
                v-model="header.key" 
                type="text" 
                placeholder="请求头名称"
                class="table-input"
              />
            </td>
            <td>
              <input 
                v-model="header.value" 
                type="text" 
                placeholder="请求头值"
                class="table-input"
              />
            </td>
            <td>
              <button @click="removeHeader(index)" class="btn-remove">-</button>
            </td>
          </tr>
        </tbody>
      </table>
      <button @click="addHeader" class="btn-add">+ 添加请求头</button>
    </div>

    <!-- 请求体 -->
    <div v-show="activeTab === 'body'" class="body-container">
      <div class="body-type">
        <label>
          <input type="radio" v-model="bodyType" value="json" /> JSON
        </label>
        <label>
          <input type="radio" v-model="bodyType" value="text" /> Text
        </label>
      </div>
      <textarea 
        v-model="requestBody" 
        placeholder='例如: {"name": "John", "age": 30}'
        class="body-textarea"
        rows="10"
      ></textarea>
    </div>

    <!-- 响应区域 -->
    <div class="response-section">
      <div class="response-header">
        <h2>响应结果</h2>
        <span v-if="responseStatus" :class="['status', statusClass]">
          状态: {{ responseStatus }}
        </span>
        <span v-if="responseTime" class="time">
          耗时: {{ responseTime }}ms
        </span>
      </div>
      
      <div v-if="loading" class="loading">请求中...</div>
      
      <div v-if="error" class="error">
        <strong>错误:</strong> {{ error }}
      </div>
      
      <div v-if="response" class="response-content">
        <pre>{{ formattedResponse }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const message = ref('API 接口测试工具');

// 请求配置
const requestMethod = ref('GET');
const apiUrl = ref('https://jsonplaceholder.typicode.com/users/1');
const activeTab = ref('params');

// Query 参数
const queryParams = ref([
  { key: '', value: '', enabled: true }
]);

// 请求头
const headers = ref([
  { key: 'Content-Type', value: 'application/json', enabled: true }
]);

// 请求体
const bodyType = ref('json');
const requestBody = ref('');

// 响应数据
const response = ref(null);
const responseStatus = ref('');
const responseTime = ref(null);
const loading = ref(false);
const error = ref('');

// 添加/删除参数
const addParam = () => {
  queryParams.value.push({ key: '', value: '', enabled: true });
};

const removeParam = (index) => {
  if (queryParams.value.length > 1) {
    queryParams.value.splice(index, 1);
  }
};

// 添加/删除请求头
const addHeader = () => {
  headers.value.push({ key: '', value: '', enabled: true });
};

const removeHeader = (index) => {
  if (headers.value.length > 1) {
    headers.value.splice(index, 1);
  }
};

// 构建完整URL
const buildUrl = () => {
  let url = apiUrl.value;
  const enabledParams = queryParams.value.filter(p => p.enabled && p.key);
  
  if (enabledParams.length > 0) {
    const params = new URLSearchParams();
    enabledParams.forEach(p => params.append(p.key, p.value));
    url += (url.includes('?') ? '&' : '?') + params.toString();
  }
  
  return url;
};

// 构建请求头
const buildHeaders = () => {
  const headersObj = {};
  headers.value
    .filter(h => h.enabled && h.key)
    .forEach(h => {
      headersObj[h.key] = h.value;
    });
  return headersObj;
};

// 发送请求
const sendRequest = async () => {
  loading.value = true;
  error.value = '';
  response.value = null;
  responseStatus.value = '';
  responseTime.value = null;
  
  const startTime = Date.now();
  
  try {
    const url = buildUrl();
    const options = {
      method: requestMethod.value,
      headers: buildHeaders()
    };
    
    // 添加请求体（如果不是GET请求）
    if (requestMethod.value !== 'GET' && requestBody.value) {
      options.body = bodyType.value === 'json' 
        ? requestBody.value 
        : requestBody.value;
    }
    
    const res = await fetch(url, options);
    responseStatus.value = `${res.status} ${res.statusText}`;
    responseTime.value = Date.now() - startTime;
    
    const contentType = res.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      response.value = await res.json();
    } else {
      response.value = await res.text();
    }
    
  } catch (err) {
    error.value = err.message;
    responseTime.value = Date.now() - startTime;
  } finally {
    loading.value = false;
  }
};

// 格式化响应
const formattedResponse = computed(() => {
  if (!response.value) return '';
  if (typeof response.value === 'string') return response.value;
  return JSON.stringify(response.value, null, 2);
});

// 状态码样式
const statusClass = computed(() => {
  const status = parseInt(responseStatus.value);
  if (status >= 200 && status < 300) return 'success';
  if (status >= 400) return 'error';
  return '';
});
</script>

<style scoped>
.api-tester {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
  margin-bottom: 20px;
}

.request-section {
  margin-bottom: 20px;
}

.request-line {
  display: flex;
  gap: 10px;
}

.method-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.url-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.send-btn {
  padding: 8px 24px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.send-btn:hover {
  background: #45a049;
}

.tabs {
  display: flex;
  gap: 5px;
  margin-bottom: 10px;
  border-bottom: 2px solid #ddd;
}

.tab {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  border-bottom: 3px solid transparent;
}

.tab.active {
  border-bottom-color: #4CAF50;
  font-weight: bold;
}

.table-container {
  margin-bottom: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
}

.param-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 10px;
}

.param-table th {
  background: #f5f5f5;
  padding: 8px;
  text-align: left;
  border-bottom: 2px solid #ddd;
  font-size: 14px;
}

.param-table td {
  padding: 5px;
  border-bottom: 1px solid #eee;
}

.table-input {
  width: 100%;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 3px;
  font-size: 13px;
}

.btn-add {
  padding: 6px 16px;
  background: #2196F3;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 13px;
}

.btn-add:hover {
  background: #0b7dda;
}

.btn-remove {
  padding: 4px 10px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}

.btn-remove:hover {
  background: #da190b;
}

.body-container {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  margin-bottom: 20px;
}

.body-type {
  margin-bottom: 10px;
}

.body-type label {
  margin-right: 15px;
  font-size: 14px;
}

.body-textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  resize: vertical;
}

.response-section {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  background: #f9f9f9;
}

.response-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.response-header h2 {
  margin: 0;
  font-size: 18px;
}

.status {
  padding: 4px 12px;
  border-radius: 3px;
  font-size: 13px;
  font-weight: bold;
}

.status.success {
  background: #d4edda;
  color: #155724;
}

.status.error {
  background: #f8d7da;
  color: #721c24;
}

.time {
  color: #666;
  font-size: 13px;
}

.loading {
  padding: 20px;
  text-align: center;
  color: #666;
}

.error {
  padding: 15px;
  background: #f8d7da;
  color: #721c24;
  border-radius: 4px;
  margin-bottom: 10px;
}

.response-content {
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  overflow-x: auto;
}

.response-content pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
