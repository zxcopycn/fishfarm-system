"""
API测试文件
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "智能渔场环境控制监测系统"
    assert response.json()["status"] == "running"


def test_health_check():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_device_list():
    """测试设备列表API"""
    response = client.get("/api/devices/list")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_alarm_rules():
    """测试预警规则API"""
    response = client.get("/api/alarms/rules")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_alarm_records():
    """测试预警记录API"""
    response = client.get("/api/alarms/records?days=1")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_control_devices():
    """测试控制设备API"""
    response = client.get("/api/control/devices")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_sensor_latest():
    """测试最新传感器数据API"""
    response = client.get("/api/sensor/latest?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
