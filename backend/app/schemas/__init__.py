"""
参数验证模型
使用Pydantic进行请求和响应的数据验证
"""

from pydantic import BaseModel, Field, validator, PositiveInt
from typing import Optional, List
from datetime import datetime


# ==================== 通用响应模型 ====================

class ResponseBase(BaseModel):
    """通用响应基类"""
    code: int = Field(200, description="响应码")
    message: str = Field("success", description="响应消息")
    data: Optional[dict] = Field(None, description="响应数据")


class ResponseModel(BaseModel):
    """通用响应模型"""
    code: int
    message: str
    data: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {}
            }
        }


# ==================== 设备相关模型 ====================

class DeviceTypeCreate(BaseModel):
    """创建设备类型"""
    name: str = Field(..., min_length=1, max_length=50, description="设备类型名称")
    code: str = Field(..., min_length=1, max_length=50, description="设备类型代码")

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("设备类型名称不能为空")
        return v.strip()

    @validator('code')
    def validate_code(cls, v):
        if not v or not v.strip():
            raise ValueError("设备类型代码不能为空")
        return v.strip().lower()


class DeviceTypeResponse(BaseModel):
    """设备类型响应"""
    id: int
    name: str
    code: str
    status: int
    created_at: datetime

    class Config:
        from_attributes = True


class DeviceCreate(BaseModel):
    """创建设备"""
    device_name: str = Field(..., min_length=1, max_length=100, description="设备名称")
    device_type_id: PositiveInt = Field(..., description="设备类型ID")
    location: Optional[str] = Field(None, max_length=200, description="安装位置")
    ip_address: Optional[str] = Field(None, max_length=50, description="IP地址")
    mqtt_topic: Optional[str] = Field(None, max_length=200, description="MQTT主题")

    @validator('device_name')
    def validate_device_name(cls, v):
        if not v or not v.strip():
            raise ValueError("设备名称不能为空")
        return v.strip()


class DeviceResponse(BaseModel):
    """设备响应"""
    id: int
    device_name: str
    device_type_id: int
    device_type_name: Optional[str] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None
    mqtt_topic: Optional[str] = None
    status: int
    current_value: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== 传感器数据模型 ====================

class SensorDataCreate(BaseModel):
    """创建传感器数据"""
    device_id: PositiveInt = Field(..., description="设备ID，必须大于0")
    temperature: Optional[float] = Field(None, ge=-50, le=100, description="温度(℃)")
    ph: Optional[float] = Field(None, ge=0, le=14, description="PH值")
    ammonia: Optional[float] = Field(None, ge=0, le=10, description="氨氮(mg/L)")
    nitrite: Optional[float] = Field(None, ge=0, le=5, description="亚盐(mg/L)")
    oxygen: Optional[float] = Field(None, ge=0, le=20, description="溶氧量(mg/L)")
    raw_value: str = Field("", max_length=5000, description="原始数据")

    @validator('temperature')
    def validate_temperature(cls, v):
        if v is not None and (v < -50 or v > 100):
            raise ValueError("温度范围必须在-50℃到100℃之间")
        return v

    @validator('ph')
    def validate_ph(cls, v):
        if v is not None and (v < 0 or v > 14):
            raise ValueError("PH值范围必须在0到14之间")
        return v

    @validator('ammonia')
    def validate_ammonia(cls, v):
        if v is not None and (v < 0 or v > 10):
            raise ValueError("氨氮值必须在0到10 mg/L之间")
        return v

    @validator('nitrite')
    def validate_nitrite(cls, v):
        if v is not None and (v < 0 or v > 5):
            raise ValueError("亚盐值必须在0到5 mg/L之间")
        return v

    @validator('oxygen')
    def validate_oxygen(cls, v):
        if v is not None and (v < 0 or v > 20):
            raise ValueError("溶氧量必须在0到20 mg/L之间")
        return v

    @validator('raw_value')
    def validate_raw_value(cls, v):
        if v and len(v) > 5000:
            raise ValueError("原始数据长度不能超过5000字符")
        return v


class SensorDataResponse(BaseModel):
    """传感器数据响应"""
    id: int
    device_id: int
    device_name: Optional[str] = None
    temperature: Optional[float] = None
    ph: Optional[float] = None
    ammonia: Optional[float] = None
    nitrite: Optional[float] = None
    oxygen: Optional[float] = None
    raw_value: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 预警相关模型 ====================

class AlarmRuleCreate(BaseModel):
    """创建预警规则"""
    device_id: Optional[PositiveInt] = Field(None, description="设备ID（NULL表示全局规则）")
    rule_name: str = Field(..., min_length=1, max_length=100, description="规则名称")
    sensor_type: Optional[str] = Field(None, max_length=50, description="传感器类型")
    threshold_type: str = Field(..., description="阈值类型：min-最小值，max-最大值，range-范围")
    threshold_value: float = Field(..., description="阈值数值")
    level: str = Field(default="提醒", description="预警级别：提醒/警告/危险")

    @validator('threshold_type')
    def validate_threshold_type(cls, v):
        if v not in ['min', 'max', 'range']:
            raise ValueError("阈值类型必须是min、max或range")
        return v

    @validator('level')
    def validate_level(cls, v):
        if v not in ['提醒', '警告', '危险']:
            raise ValueError("预警级别必须是提醒、警告或危险")
        return v


class AlarmRuleResponse(BaseModel):
    """预警规则响应"""
    id: int
    device_id: Optional[int] = None
    rule_name: str
    sensor_type: Optional[str] = None
    threshold_type: str
    threshold_value: float
    level: str
    is_enabled: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlarmRecordResponse(BaseModel):
    """预警记录响应"""
    id: int
    device_id: Optional[int] = None
    rule_id: Optional[int] = None
    alarm_level: str
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    message: Optional[str] = None
    is_resolved: int
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 控制设备模型 ====================

class ControlDeviceCreate(BaseModel):
    """创建控制设备"""
    device_name: str = Field(..., min_length=1, max_length=100, description="设备名称")
    device_type: str = Field(..., min_length=1, max_length=50, description="设备类型")
    location: Optional[str] = Field(None, max_length=200, description="安装位置")
    mqtt_topic: Optional[str] = Field(None, max_length=200, description="MQTT主题")

    @validator('device_name')
    def validate_device_name(cls, v):
        if not v or not v.strip():
            raise ValueError("设备名称不能为空")
        return v.strip()


class ControlDeviceResponse(BaseModel):
    """控制设备响应"""
    id: int
    device_name: str
    device_type: str
    location: Optional[str] = None
    status: int
    mqtt_topic: Optional[str] = None
    current_power: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ControlRecordResponse(BaseModel):
    """控制记录响应"""
    id: int
    device_id: int
    device_name: Optional[str] = None
    action: str
    target_value: Optional[float] = None
    actual_value: Optional[float] = None
    operator: Optional[str] = None
    remark: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 用户认证模型 ====================

class UserLogin(BaseModel):
    """用户登录"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=1, description="密码")

    @validator('username')
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError("用户名不能为空")
        return v.strip()

    @validator('password')
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError("密码长度至少为6位")
        return v


class UserRegister(BaseModel):
    """用户注册"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    role: str = Field(default="operator", description="角色：admin-管理员，operator-操作员")

    @validator('username')
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError("用户名不能为空")
        return v.strip()

    @validator('password')
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError("密码长度至少为6位")
        return v


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str
    token_type: str = "bearer"
    user_info: Optional[dict] = None


# ==================== 备忘提醒模型 ====================

class ReminderCreate(BaseModel):
    """创建提醒"""
    title: str = Field(..., min_length=1, max_length=200, description="提醒标题")
    content: Optional[str] = Field(None, description="提醒内容")
    reminder_time: datetime = Field(..., description="提醒时间")

    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("提醒标题不能为空")
        return v.strip()


class ReminderResponse(BaseModel):
    """提醒响应"""
    id: int
    title: str
    content: Optional[str] = None
    reminder_time: datetime
    is_completed: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
