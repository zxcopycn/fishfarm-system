#!/usr/bin/env python3
"""
渔场系统Web版 - 基于Flask的Web界面
可以直接在浏览器中体验完整功能
"""

from flask import Flask, render_template, jsonify, request
import requests
from datetime import datetime
import json

app = Flask(__name__)

# API服务地址
BACKEND_URL = "http://127.0.0.1:8003"

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/health')
def health():
    """健康检查"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.json()
    except:
        return {"status": "error", "service": "连接失败"}

@app.route('/api/devices')
def get_devices():
    """获取设备列表"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/devices/list", timeout=5)
        return response.json()
    except:
        return []

@app.route('/api/sensors')
def get_sensors():
    """获取传感器数据"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/sensor/latest", timeout=5)
        return response.json()
    except:
        return []

@app.route('/api/alarms/rules')
def get_alarm_rules():
    """获取预警规则"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/alarms/rules", timeout=5)
        return response.json()
    except:
        return []

@app.route('/api/alarms/records')
def get_alarm_records():
    """获取预警记录"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/alarms/records", timeout=5)
        return response.json()
    except:
        return []

@app.route('/api/reminders')
def get_reminders():
    """获取提醒列表"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/reminders", timeout=5)
        return response.json()
    except:
        return []

@app.route('/api/production')
def get_production():
    """获取生产记录"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/production/list", timeout=5)
        return response.json()
    except:
        return []

@app.route('/dashboard')
def dashboard():
    """仪表盘页面"""
    return render_template('dashboard.html')

@app.route('/devices')
def devices():
    """设备管理页面"""
    return render_template('devices.html')

@app.route('/alarms')
def alarms():
    """预警管理页面"""
    return render_template('alarms.html')

@app.route('/reminders')
def reminders():
    """提醒管理页面"""
    return render_template('reminders.html')

@app.route('/production')
def production():
    """生产记录页面"""
    return render_template('production.html')

if __name__ == '__main__':
    print("🚀 渔场系统Web版启动中...")
    print("📍 访问地址: http://localhost:5000")
    print("📱 移动端访问: http://192.168.1.200:5000 (替换为实际IP)")
    print("🔄 自动检测后端API状态...")
    
    # 测试后端连接
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端API连接正常")
        else:
            print("⚠️ 后端API连接异常")
    except:
        print("❌ 无法连接到后端API")
    
    app.run(host='0.0.0.0', port=5000, debug=False)