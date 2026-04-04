"""
测试认证功能
"""
import pytest
from app.auth import (
    get_password_hash, verify_password,
    create_access_token
)
from app.schemas import (
    UserLogin, UserRegister, SensorDataCreate,
    DeviceCreate, AlarmRuleCreate
)


def test_password_hashing():
    """测试密码哈希和验证"""
    password = "test_password_123"
    
    # 生成哈希
    password_hash = get_password_hash(password)
    
    # 验证密码
    assert verify_password(password, password_hash) is True
    assert verify_password("wrong_password", password_hash) is False


def test_create_access_token():
    """测试创建访问令牌"""
    data = {"sub": "testuser", "role": "admin"}
    
    # 创建token
    token = create_access_token(data)
    
    # 验证token不为空
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_user_login_validation():
    """测试用户登录验证"""
    # 正确的数据
    valid_login = UserLogin(username="testuser", password="password123")
    assert valid_login.username == "testuser"
    assert valid_login.password == "password123"
    
    # 空用户名
    with pytest.raises(ValueError):
        UserLogin(username="", password="password123")
    
    # 空密码
    with pytest.raises(ValueError):
        UserLogin(username="testuser", password="")


def test_user_register_validation():
    """测试用户注册验证"""
    # 正确的数据
    valid_register = UserRegister(
        username="testuser",
        password="password123",
        real_name="Test User",
        role="operator"
    )
    assert valid_register.username == "testuser"
    assert valid_register.password == "password123"
    
    # 空用户名
    with pytest.raises(ValueError):
        UserRegister(username="", password="password123")
    
    # 密码太短
    with pytest.raises(ValueError):
        UserRegister(username="testuser", password="123")


def test_sensor_data_validation():
    """测试传感器数据验证"""
    # 正确的数据
    valid_data = SensorDataCreate(
        device_id=1,
        temperature=25.5,
        ph=7.2,
        ammonia=0.5,
        nitrite=0.1,
        oxygen=8.5
    )
    assert valid_data.device_id == 1
    assert valid_data.temperature == 25.5
    
    # 温度超出范围
    with pytest.raises(ValueError):
        SensorDataCreate(device_id=1, temperature=150)
    
    # PH值超出范围
    with pytest.raises(ValueError):
        SensorDataCreate(device_id=1, ph=15)
    
    # 氨氮值超出范围
    with pytest.raises(ValueError):
        SensorDataCreate(device_id=1, ammonia=15)


def test_device_create_validation():
    """测试设备创建验证"""
    # 正确的数据
    valid_device = DeviceCreate(
        device_name="温度传感器1",
        device_type_id=1,
        location="鱼池1号",
        ip_address="192.168.1.100"
    )
    assert valid_device.device_name == "温度传感器1"
    
    # 空设备名称
    with pytest.raises(ValueError):
        DeviceCreate(device_name="", device_type_id=1)


def test_alarm_rule_validation():
    """测试预警规则验证"""
    # 正确的数据
    valid_rule = AlarmRuleCreate(
        rule_name="温度预警",
        sensor_type="temperature",
        threshold_type="max",
        threshold_value=30.0,
        level="警告"
    )
    assert valid_rule.rule_name == "温度预警"
    
    # 错误的阈值类型
    with pytest.raises(ValueError):
        AlarmRuleCreate(
            rule_name="温度预警",
            threshold_type="invalid",
            threshold_value=30.0
        )
    
    # 错误的预警级别
    with pytest.raises(ValueError):
        AlarmRuleCreate(
            rule_name="温度预警",
            threshold_type="max",
            threshold_value=30.0,
            level="无效级别"
        )
