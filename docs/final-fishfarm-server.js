#!/usr/bin/env node
/**
 * 渔场系统API服务器 - 正式版
 * 支持自动获取本机IP地址
 */

const http = require('http');
const url = require('url');

// 模拟数据
const mockData = {
  devices: [
    {
      id: 1,
      device_name: "温度传感器-1",
      device_type: "温度传感器",
      device_type_id: 1,
      device_type_name: "传感器",
      current_value: 25.5,
      status: 1,
      created_at: "2026-04-17T00:00:00Z",
      updated_at: "2026-04-17T00:00:00Z"
    },
    {
      id: 2,
      device_name: "PH传感器-1",
      device_type: "PH传感器",
      device_type_id: 2,
      device_type_name: "传感器",
      current_value: 7.2,
      status: 1,
      created_at: "2026-04-17T00:00:00Z",
      updated_at: "2026-04-17T00:00:00Z"
    },
    {
      id: 3,
      device_name: "溶氧传感器-1",
      device_type: "溶氧传感器",
      device_type_id: 3,
      device_type_name: "传感器",
      current_value: 8.5,
      status: 1,
      created_at: "2026-04-17T00:00:00Z",
      updated_at: "2026-04-17T00:00:00Z"
    },
    {
      id: 4,
      device_name: "氨氮传感器-1",
      device_type: "氨氮传感器",
      device_type_id: 4,
      device_type_name: "传感器",
      current_value: 0.3,
      status: 1,
      created_at: "2026-04-17T00:00:00Z",
      updated_at: "2026-04-17T00:00:00Z"
    },
    {
      id: 5,
      device_name: "亚硝酸盐传感器-1",
      device_type: "亚硝酸盐传感器",
      device_type_id: 5,
      device_type_name: "传感器",
      current_value: 0.15,
      status: 1,
      created_at: "2026-04-17T00:00:00Z",
      updated_at: "2026-04-17T00:00:00Z"
    },
    {
      id: 6,
      device_name: "饲料投喂器-1",
      device_type: "饲料投喂器",
      device_type_id: 6,
      device_type_name: "控制设备",
      current_value: 0,
      status: 1,
      created_at: "2026-04-17T00:00:00Z",
      updated_at: "2026-04-17T00:00:00Z"
    },
    {
      id: 7,
      device_name: "增氧机-1",
      device_type: "增氧机",
      device_type_id: 7,
      device_type_name: "控制设备",
      current_value: 1,
      status: 1,
      created_at: "2026-04-17T00:00:00Z",
      updated_at: "2026-04-17T00:00:00Z"
    },
    {
      id: 8,
      device_name: "排水阀-1",
      device_type: "排水阀",
      device_type_id: 8,
      device_type_name: "控制设备",
      current_value: 0,
      status: 1,
      created_at: "2026-04-17T00:00:00Z",
      updated_at: "2026-04-17T00:00:00Z"
    }
  ],
  sensorData: [
    {
      id: 1,
      device_id: 1,
      device_name: "温度传感器-1",
      temperature: 25.5,
      humidity: 65.0,
      ph: 7.2,
      ammonia: 0.5,
      nitrite: 0.2,
      oxygen: 8.1,
      created_at: "2026-04-17T10:00:00Z"
    },
    {
      id: 2,
      device_id: 2,
      device_name: "PH传感器-1",
      temperature: 25.3,
      humidity: 62.5,
      ph: 7.4,
      ammonia: 0.6,
      nitrite: 0.3,
      oxygen: 8.0,
      created_at: "2026-04-17T10:00:00Z"
    },
    {
      id: 3,
      device_id: 3,
      device_name: "溶氧传感器-1",
      temperature: 25.2,
      humidity: 68.0,
      ph: 7.3,
      ammonia: 0.4,
      nitrite: 0.2,
      oxygen: 8.5,
      created_at: "2026-04-17T10:00:00Z"
    },
    {
      id: 4,
      device_id: 4,
      device_name: "氨氮传感器-1",
      temperature: 25.4,
      humidity: 64.5,
      ph: 7.1,
      ammonia: 0.3,
      nitrite: 0.1,
      oxygen: 8.2,
      created_at: "2026-04-17T10:00:00Z"
    },
    {
      id: 5,
      device_id: 5,
      device_name: "亚硝酸盐传感器-1",
      temperature: 25.6,
      humidity: 63.8,
      ph: 7.5,
      ammonia: 0.2,
      nitrite: 0.15,
      oxygen: 8.3,
      created_at: "2026-04-17T10:00:00Z"
    }
  ],
  alarms: [
    {
      id: 1,
      device_id: 1,
      device_name: "温度传感器-1",
      alarm_rule_id: 1,
      alarm_rule_name: "温度过高",
      alarm_type: "warning",
      alarm_level: "warning",
      message: "温度超过上限(30°C)",
      trigger_value: "31.5°C",
      threshold_value: "30°C",
      is_resolved: false,
      resolved_at: null,
      resolved_by: null,
      created_at: "2026-04-16T14:30:00Z"
    },
    {
      id: 2,
      device_id: 2,
      device_name: "PH传感器-1",
      alarm_rule_id: 2,
      alarm_rule_name: "PH值异常",
      alarm_type: "danger",
      alarm_level: "danger",
      message: "PH值超出安全范围(<6.5)",
      trigger_value: "6.2",
      threshold_value: "6.5",
      is_resolved: false,
      resolved_at: null,
      resolved_by: null,
      created_at: "2026-04-16T09:15:00Z"
    }
  ],
  productionRecords: [
    {
      id: 1,
      fish_type: "草鱼",
      quantity: 1000,
      spawn_date: "2026-03-01T00:00:00Z",
      hatch_date: "2026-03-15T00:00:00Z",
      growth_stage: "鱼苗",
      average_weight: 0.5,
      average_length: 5.0,
      feed_amount: 10.5,
      remark: "第一批入池",
      created_at: "2026-03-01T00:00:00Z",
      updated_at: "2026-04-17T00:00:00Z"
    },
    {
      id: 2,
      fish_type: "鲫鱼",
      quantity: 500,
      spawn_date: "2026-03-10T00:00:00Z",
      hatch_date: "2026-03-25T00:00:00Z",
      growth_stage: "鱼苗",
      average_weight: 0.3,
      average_length: 4.0,
      feed_amount: 5.0,
      remark: "第二批入池",
      created_at: "2026-03-10T00:00:00Z",
      updated_at: "2026-04-17T00:00:00Z"
    }
  ],
  reminders: [
    {
      id: 1,
      title: "饲料采购",
      content: "联系供应商采购下个月饲料",
      is_completed: false,
      reminder_time: "2026-04-25T09:00:00Z",
      created_at: "2026-04-15T00:00:00Z"
    },
    {
      id: 2,
      title: "设备维护",
      content: "检查增氧机运行状态",
      is_completed: true,
      reminder_time: "2026-04-20T10:00:00Z",
      created_at: "2026-04-14T00:00:00Z"
    }
  ]
};

// 创建HTTP服务器
const server = http.createServer((req, res) => {
  // 设置CORS头
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  const { pathname, query } = url.parse(req.url, true);
  const method = req.method;

  // 处理OPTIONS请求
  if (method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // 设置响应头
  res.setHeader('Content-Type', 'application/json');

  try {
    // 健康检查
    if (pathname === '/health') {
      res.writeHead(200);
      res.end(JSON.stringify({
        status: 'healthy',
        service: 'fishfarm-api',
        message: '服务器正常运行'
      }));
      return;
    }

    // 获取设备列表
    if (pathname === '/api/devices') {
      res.writeHead(200);
      res.end(JSON.stringify(mockData.devices));
      return;
    }

    // 获取传感器数据
    if (pathname === '/api/sensor-data') {
      res.writeHead(200);
      res.end(JSON.stringify(mockData.sensorData));
      return;
    }

    // 获取最新传感器数据
    if (pathname === '/api/sensor/latest') {
      res.writeHead(200);
      res.end(JSON.stringify(mockData.sensorData));
      return;
    }

    // 获取预警规则
    if (pathname === '/api/alarms') {
      res.writeHead(200);
      res.end(JSON.stringify(mockData.alarms));
      return;
    }

    // 获取预警记录
    if (pathname === '/api/alarms/records') {
      res.writeHead(200);
      res.end(JSON.stringify(mockData.alarms));
      return;
    }

    // 解决预警
    if (pathname.startsWith('/api/alarms/records/') && pathname.endsWith('/resolve')) {
      res.writeHead(200);
      res.end(JSON.stringify({ status: 'success', message: '预警已解决' }));
      return;
    }

    // 获取生产记录
    if (pathname === '/api/production-records') {
      res.writeHead(200);
      res.end(JSON.stringify(mockData.productionRecords));
      return;
    }

    // 获取提醒列表
    if (pathname === '/api/reminders') {
      res.writeHead(200);
      res.end(JSON.stringify(mockData.reminders));
      return;
    }

    // BLE传感器数据接收 (POST)
    if (pathname === '/api/ble-data' && method === 'POST') {
      let body = '';
      req.on('data', chunk => { body += chunk; });
      req.on('end', () => {
        try {
          const data = JSON.parse(body);
          console.log('[BLE数据接收]', new Date().toISOString(), data);
          
          // 更新传感器数据
          const bleDevice = mockData.devices.find(d => d.id === data.device_id);
          if (bleDevice) {
            bleDevice.current_value = data.temperature;
            bleDevice.updated_at = new Date().toISOString();
          }
          
          // 添加到sensorData历史
          const newRecord = {
            id: mockData.sensorData.length + 1,
            device_id: data.device_id,
            device_name: bleDevice ? bleDevice.device_name : 'BLE传感器',
            temperature: data.temperature,
            humidity: data.humidity,
            battery: data.battery,
            ph: data.ph || null,
            ammonia: data.ammonia || null,
            nitrite: data.nitrite || null,
            oxygen: data.oxygen || null,
            created_at: new Date().toISOString()
          };
          mockData.sensorData.push(newRecord);
          
          // 低电量报警检查
          if (data.battery && data.battery < 20) {
            // 检查是否已有未解决的重试报警
            const existingAlarm = mockData.alarms.find(
              a => a.alarm_rule_name === '电量过低' && 
                   a.device_id === data.device_id && 
                   !a.is_resolved
            );
            
            if (!existingAlarm) {
              const lowBatteryAlarm = {
                id: mockData.alarms.length + 1,
                device_id: data.device_id,
                device_name: bleDevice ? bleDevice.device_name : 'BLE传感器',
                alarm_rule_id: 100,  // 专用规则ID
                alarm_rule_name: '电量过低',
                alarm_type: 'warning',
                alarm_level: 'warning',
                message: `BLE传感器电量过低 (${data.battery}%)`,
                trigger_value: `${data.battery}%`,
                threshold_value: '20%',
                is_resolved: false,
                resolved_at: null,
                resolved_by: null,
                created_at: new Date().toISOString()
              };
              mockData.alarms.push(lowBatteryAlarm);
              console.log('[⚠️ 低电量报警]', data.battery + '%');
            }
          }
          
          res.writeHead(200);
          res.end(JSON.stringify({ 
            success: true, 
            message: '数据接收成功',
            id: newRecord.id 
          }));
        } catch (e) {
          console.error('BLE数据处理错误:', e);
          res.writeHead(400);
          res.end(JSON.stringify({ success: false, message: '数据格式错误' }));
        }
      });
      return;
    }

    // 404
    res.writeHead(404);
    res.end(JSON.stringify({ error: 'Not Found', path: pathname }));

  } catch (error) {
    console.error('请求处理错误:', error);
    res.writeHead(500);
    res.end(JSON.stringify({ error: 'Internal Server Error' }));
  }
});

// 自动获取本机IP地址
function getLocalIP() {
  const os = require('os');
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === 'IPv4' && !iface.internal) {
        return iface.address;
      }
    }
  }
  return '127.0.0.1';
}

// 启动服务器
const PORT = 8080;
const LOCAL_IP = getLocalIP();

server.listen(PORT, '0.0.0.0', () => {
  console.log('');
  console.log('🚀 渔场API服务器已启动');
  console.log('📱 局域网地址: http://' + LOCAL_IP + ':' + PORT);
  console.log('🌐 本地地址: http://localhost:' + PORT);
  console.log('💊 健康检查: http://localhost:' + PORT + '/health');
  console.log('📋 设备列表: http://localhost:' + PORT + '/api/devices');
  console.log('🌡️ 传感器数据: http://localhost:' + PORT + '/api/sensor-data');
  console.log('⚠️  预警信息: http://localhost:' + PORT + '/api/alarms');
  console.log('📱 移动端测试: http://' + LOCAL_IP + ':' + PORT);
  console.log('');
});

server.on('error', (error) => {
  if (error.code === 'EADDRINUSE') {
    console.error('端口 ' + PORT + ' 已被占用');
  } else {
    console.error('服务器错误:', error);
  }
});

// 定时更新传感器数据 - 已禁用
// 注意：真实数据由BLE采集程序通过 /api/ble-data 上报
// setInterval(() => {
//   mockData.sensorData.forEach(sensor => {
//     sensor.temperature = (20 + Math.random() * 15).toFixed(1);
//     sensor.ph = (6.5 + Math.random() * 2).toFixed(1);
//     sensor.ammonia = (0.1 + Math.random() * 1).toFixed(2);
//     sensor.nitrite = (0.05 + Math.random() * 0.5).toFixed(2);
//     sensor.oxygen = (7 + Math.random() * 2).toFixed(1);
//     sensor.created_at = new Date().toISOString();
//   });
// 
//   mockData.devices.forEach(device => {
//     const sensorData = mockData.sensorData.find(s => s.device_id === device.id);
//     if (sensorData) {
//       device.current_value = parseFloat(sensorData.temperature);
//     }
//     device.updated_at = new Date().toISOString();
//   });
// }, 30000);

console.log('✅ 服务器配置完成，等待连接...');
console.log('📡 真实数据由BLE采集程序通过 POST /api/ble-data 上报');
