#!/usr/bin/env python3
"""
渔场系统端到端测试脚本
模拟移动端APP与后端的完整交互流程
"""

import sys
import os
import json
import time
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 添加路径
sys.path.insert(0, '/home/node/.openclaw/workspace/fishfarm-system/backend')

class EndToEndTest:
    """端到端测试类"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_url = f"{self.base_url}/api/v1"
        self.test_results = []
        self.device_id = None
        self.user_id = None
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{'✅' if status == 'PASS' else '❌'} {test_name}")
        if details:
            print(f"   {details}")
    
    def test_1_backend_health(self) -> bool:
        """测试1: 后端服务健康检查"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'healthy':
                    self.log_test("后端服务健康检查", "PASS", f"服务状态: {data['status']}")
                    return True
            self.log_test("后端服务健康检查", "FAIL", f"响应状态码: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("后端服务健康检查", "FAIL", f"连接失败: {str(e)}")
            return False
    
    def test_2_api_documentation(self) -> bool:
        """测试2: API文档访问"""
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=10)
            if response.status_code == 200 and "swagger" in response.text.lower():
                self.log_test("API文档访问", "PASS", "Swagger文档可访问")
                return True
            self.log_test("API文档访问", "FAIL", f"响应状态码: {response.status_code}")
            return False
        except Exception as e:
            self.log_test("API文档访问", "FAIL", f"文档访问失败: {str(e)}")
            return False
    
    def test_3_database_connection(self) -> bool:
        """测试3: 数据库连接"""
        try:
            conn = sqlite3.connect('/home/node/.openclaw/workspace/fishfarm-system/backend/fishfarm.db')
            cursor = conn.cursor()
            
            # 测试基本查询
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            required_tables = ['devices', 'sensor_data', 'users', 'reminders']
            existing_tables = [table[0] for table in tables]
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            if not missing_tables:
                self.log_test("数据库连接", "PASS", f"数据库连接正常，表数量: {len(tables)}")
                conn.close()
                return True
            else:
                self.log_test("数据库连接", "FAIL", f"缺少表: {missing_tables}")
                conn.close()
                return False
                
        except Exception as e:
            self.log_test("数据库连接", "FAIL", f"数据库连接失败: {str(e)}")
            return False
    
    def test_4_device_management(self) -> bool:
        """测试4: 设备管理API"""
        try:
            # 添加设备
            device_data = {
                "device_name": "测试温度传感器",
                "device_type_id": 1,
                "location": "测试区域",
                "status": 1
            }
            
            response = requests.post(f"{self.api_url}/devices", json=device_data, timeout=10)
            if response.status_code == 200:
                device_info = response.json()
                self.device_id = device_info.get("id")
                self.log_test("设备添加", "PASS", f"设备ID: {self.device_id}")
                
                # 获取设备列表
                response = requests.get(f"{self.api_url}/devices/list", timeout=10)
                if response.status_code == 200:
                    devices = response.json()
                    if len(devices) > 0:
                        self.log_test("设备列表查询", "PASS", f"设备数量: {len(devices)}")
                        return True
                self.log_test("设备列表查询", "FAIL", "设备列表为空")
                return False
            else:
                self.log_test("设备添加", "FAIL", f"添加失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("设备管理", "FAIL", f"API调用失败: {str(e)}")
            return False
    
    def test_5_sensor_data(self) -> bool:
        """测试5: 传感器数据API"""
        try:
            # 模拟传感器数据
            if not self.device_id:
                self.log_test("传感器数据", "FAIL", "缺少设备ID")
                return False
                
            sensor_data = {
                "device_id": self.device_id,
                "temperature": 25.5,
                "ph": 7.2,
                "ammonia": 0.1,
                "nitrite": 0.05,
                "oxygen": 8.3
            }
            
            response = requests.post(f"{self.api_url}/sensor/data", json=sensor_data, timeout=10)
            if response.status_code == 200:
                self.log_test("传感器数据添加", "PASS", "数据添加成功")
                
                # 获取最新数据
                response = requests.get(f"{self.api_url}/sensor/latest", timeout=10)
                if response.status_code == 200:
                    latest_data = response.json()
                    if latest_data:
                        self.log_test("最新传感器数据", "PASS", "数据获取成功")
                        return True
                self.log_test("最新传感器数据", "FAIL", "数据获取失败")
                return False
            else:
                self.log_test("传感器数据添加", "FAIL", f"添加失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("传感器数据", "FAIL", f"API调用失败: {str(e)}")
            return False
    
    def test_6_alarm_system(self) -> bool:
        """测试6: 预警系统"""
        try:
            # 添加预警规则
            alarm_rule = {
                "device_id": self.device_id,
                "rule_name": "温度过高预警",
                "sensor_type": "temperature",
                "threshold_type": "max",
                "threshold_value": 30.0,
                "level": "警告"
            }
            
            response = requests.post(f"{self.api_url}/alarms/rules", json=alarm_rule, timeout=10)
            if response.status_code == 200:
                self.log_test("预警规则添加", "PASS", "规则添加成功")
                
                # 获取预警记录
                response = requests.get(f"{self.api_url}/alarms/records", timeout=10)
                if response.status_code == 200:
                    records = response.json()
                    self.log_test("预警记录查询", "PASS", f"记录数量: {len(records)}")
                    return True
                self.log_test("预警记录查询", "FAIL", "记录查询失败")
                return False
            else:
                self.log_test("预警规则添加", "FAIL", f"添加失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("预警系统", "FAIL", f"API调用失败: {str(e)}")
            return False
    
    def test_7_control_system(self) -> bool:
        """测试7: 控制系统"""
        try:
            # 获取控制设备
            response = requests.get(f"{self.api_url}/control/devices", timeout=10)
            if response.status_code == 200:
                control_devices = response.json()
                if control_devices:
                    # 控制第一个设备
                    device_id = control_devices[0]["id"]
                    control_data = {
                        "action": "开启",
                        "target_value": 100
                    }
                    
                    response = requests.post(f"{self.api_url}/control/{device_id}/control", json=control_data, timeout=10)
                    if response.status_code == 200:
                        self.log_test("设备控制", "PASS", f"设备{device_id}控制成功")
                        
                        # 获取控制记录
                        response = requests.get(f"{self.api_url}/control/records", timeout=10)
                        if response.status_code == 200:
                            records = response.json()
                            self.log_test("控制记录查询", "PASS", f"记录数量: {len(records)}")
                            return True
                        self.log_test("控制记录查询", "FAIL", "记录查询失败")
                        return False
                    else:
                        self.log_test("设备控制", "FAIL", f"控制失败: {response.status_code}")
                        return False
                else:
                    self.log_test("控制设备", "FAIL", "没有找到控制设备")
                    return False
            else:
                self.log_test("控制设备查询", "FAIL", f"查询失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("控制系统", "FAIL", f"API调用失败: {str(e)}")
            return False
    
    def test_8_reminder_system(self) -> bool:
        """测试8: 提醒系统"""
        try:
            # 添加提醒
            reminder_data = {
                "title": "设备维护提醒",
                "content": "检查温度传感器电池",
                "reminder_time": (datetime.now() + timedelta(days=1)).isoformat()
            }
            
            response = requests.post(f"{self.api_url}/reminders", json=reminder_data, timeout=10)
            if response.status_code == 200:
                self.log_test("提醒添加", "PASS", "提醒添加成功")
                
                # 获取提醒列表
                response = requests.get(f"{self.api_url}/reminders", timeout=10)
                if response.status_code == 200:
                    reminders = response.json()
                    self.log_test("提醒列表查询", "PASS", f"提醒数量: {len(reminders)}")
                    return True
                self.log_test("提醒列表查询", "FAIL", "提醒查询失败")
                return False
            else:
                self.log_test("提醒添加", "FAIL", f"添加失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("提醒系统", "FAIL", f"API调用失败: {str(e)}")
            return False
    
    def test_9_real_time_api(self) -> bool:
        """测试9: 实时数据API"""
        try:
            # 测试传感器统计数据
            response = requests.get(f"{self.api_url}/sensor/statistics", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                self.log_test("传感器统计", "PASS", "统计获取成功")
                
                # 测试设备状态
                response = requests.get(f"{self.api_url}/devices/1/status", timeout=10)
                if response.status_code == 200:
                    status = response.json()
                    self.log_test("设备状态", "PASS", "状态获取成功")
                    return True
                self.log_test("设备状态", "FAIL", "状态获取失败")
                return False
            else:
                self.log_test("传感器统计", "FAIL", f"统计获取失败: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("实时数据API", "FAIL", f"API调用失败: {str(e)}")
            return False
    
    def test_10_performance(self) -> bool:
        """测试10: 性能测试"""
        try:
            import time
            
            # 测试API响应时间
            start_time = time.time()
            response = requests.get(f"{self.api_url}/devices/list", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            
            if response.status_code == 200 and response_time < 1000:
                self.log_test("API性能测试", "PASS", f"响应时间: {response_time:.2f}ms")
                return True
            else:
                self.log_test("API性能测试", "FAIL", f"响应时间: {response_time:.2f}ms，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("性能测试", "FAIL", f"性能测试失败: {str(e)}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 80)
        print("🚀 渔场系统端到端测试开始")
        print("=" * 80)
        
        test_functions = [
            ("后端服务健康检查", self.test_1_backend_health),
            ("API文档访问", self.test_2_api_documentation),
            ("数据库连接", self.test_3_database_connection),
            ("设备管理", self.test_4_device_management),
            ("传感器数据", self.test_5_sensor_data),
            ("预警系统", self.test_6_alarm_system),
            ("控制系统", self.test_7_control_system),
            ("提醒系统", self.test_8_reminder_system),
            ("实时数据API", self.test_9_real_time_api),
            ("性能测试", self.test_10_performance),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in test_functions:
            try:
                print(f"\n🧪 {test_name}...")
                if test_func():
                    passed += 1
                else:
                    failed += 1
                time.sleep(1)  # 避免请求过于频繁
            except Exception as e:
                self.log_test(test_name, "FAIL", f"测试异常: {str(e)}")
                failed += 1
        
        # 生成测试报告
        self.generate_report(passed, failed)
        
    def generate_report(self, passed: int, failed: int):
        """生成测试报告"""
        print("\n" + "=" * 80)
        print("📊 测试报告")
        print("=" * 80)
        
        total = passed + failed
        pass_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"通过率: {pass_rate:.1f}%")
        
        if pass_rate >= 80:
            print("✅ 系统状态: 优秀")
        elif pass_rate >= 60:
            print("⚠️  系统状态: 良好")
        else:
            print("❌ 系统状态: 需要改进")
        
        print("\n📋 详细测试结果:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_icon} {result['test_name']}")
            if result['details']:
                print(f"   {result['details']}")
        
        # 保存测试结果
        report_file = "/home/node/.openclaw/workspace/fishfarm-system/test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 测试报告已保存: {report_file}")
        
        print("\n" + "=" * 80)
        print("🎉 端到端测试完成!")
        print("=" * 80)


def main():
    """主函数"""
    try:
        test = EndToEndTest()
        test.run_all_tests()
        return True
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
        return False
    except Exception as e:
        print(f"\n❌ 测试运行异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)