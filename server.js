const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

// 簡單 metrics（之後可以拿來對應 SLI）
let loginRequestsTotal = 0;
let loginSuccessTotal = 0;
let loginFailTotal = 0;
let loginErrorTotal = 0;

// 登入 API
app.post('/api/login', (req, res) => {
  const { username, password } = req.body; // 密碼只用來比對，不要 log 出去
  const startTime = Date.now();

  loginRequestsTotal += 1;
  console.log(`[INFO] login_attempt username=${username}`);

  try {
    if (username === 'admin' && password === '1234') {
      loginSuccessTotal += 1;
      const latency = Date.now() - startTime;
      console.log(`[INFO] login_success username=${username} latency_ms=${latency}`);
      return res.json({ success: true, token: 'mock-secure-token-123' });
    }

    loginFailTotal += 1;
    const latency = Date.now() - startTime;
    console.warn(`[WARN] login_failed_invalid_credentials username=${username} latency_ms=${latency}`);
    return res.status(401).json({ success: false, message: '帳號或密碼錯誤' });
  } catch (err) {
    loginErrorTotal += 1;
    const latency = Date.now() - startTime;
    console.error(
      `[ERROR] login_failed_internal_error username=${username} latency_ms=${latency} error=${err.message}`
    );
    return res.status(500).json({ success: false, message: '系統錯誤，請稍後再試' });
  }
});

// 簡單 /metrics endpoint（之後 Task 1 可以截圖用）
app.get('/metrics', (req, res) => {
  res.type('text/plain').send(
    [
      `login_requests_total ${loginRequestsTotal}`,
      `login_success_total ${loginSuccessTotal}`,
      `login_fail_total ${loginFailTotal}`,
      `login_error_total ${loginErrorTotal}`
    ].join('\n')
  );
});

app.listen(PORT, () => {
  console.log(`[INFO] service_started port=${PORT} url=http://localhost:${PORT}`);
});
