-- 创建数据库
CREATE DATABASE IF NOT EXISTS fishfarm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE fishfarm;

-- 设备类型枚举
CREATE TABLE device_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL COMMENT '设备类型名称',
    code VARCHAR(50) NOT NULL COMMENT '设备类型代码',
    status TINYINT DEFAULT 1 COMMENT '状态：1-启用 0-禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_code (code)
) COMMENT '设备类型表';

-- 添加默认设备类型
INSERT INTO device_types (name, code) VALUES
('温度传感器', 'temperature'),
('PH传感器', 'ph'),
('氨氮传感器', 'ammonia'),
('亚盐传感器', 'nitrite'),
('溶氧传感器', 'dissolved_oxygen'),
('水泵', 'water_pump'),
('气泵', 'air_pump'),
('空调', 'air_conditioner'),
('排气扇', 'exhaust_fan');

-- 设备表
CREATE TABLE devices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    device_type_id INT NOT NULL COMMENT '设备类型ID',
    location VARCHAR(200) COMMENT '安装位置',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    mqtt_topic VARCHAR(200) COMMENT 'MQTT主题',
    status TINYINT DEFAULT 1 COMMENT '状态：1-在线 0-离线',
    current_value DECIMAL(10,2) COMMENT '当前值',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_type_id) REFERENCES device_types(id) ON DELETE RESTRICT,
    INDEX idx_device_type (device_type_id),
    INDEX idx_status (status)
) COMMENT '设备表';

-- 传感器数据表（实时数据）
CREATE TABLE sensor_data (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    device_id INT NOT NULL COMMENT '设备ID',
    temperature DECIMAL(5,2) COMMENT '温度(℃)',
    ph DECIMAL(4,2) COMMENT 'PH值',
    ammonia DECIMAL(6,3) COMMENT '氨氮(mg/L)',
    nitrite DECIMAL(6,3) COMMENT '亚盐(mg/L)',
    oxygen DECIMAL(5,2) COMMENT '溶氧量(mg/L)',
    raw_value TEXT COMMENT '原始数据',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_device (device_id),
    INDEX idx_time (created_at),
    INDEX idx_temperature (temperature),
    INDEX idx_ph (ph)
) COMMENT '传感器数据表（实时数据）';

-- 预警规则表
CREATE TABLE alarm_rules (
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_id INT COMMENT '设备ID（NULL表示全局规则）',
    rule_name VARCHAR(100) NOT NULL COMMENT '规则名称',
    sensor_type VARCHAR(50) COMMENT '传感器类型',
    threshold_type ENUM('min', 'max', 'range') NOT NULL COMMENT '阈值类型：min-最小值，max-最大值，range-范围',
    threshold_value DECIMAL(10,2) NOT NULL COMMENT '阈值数值',
    level ENUM('提醒', '警告', '危险') DEFAULT '提醒' COMMENT '预警级别',
    is_enabled TINYINT DEFAULT 1 COMMENT '是否启用：1-启用 0-禁用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_device (device_id),
    INDEX idx_level (level),
    INDEX idx_enabled (is_enabled)
) COMMENT '预警规则表';

-- 预警记录表
CREATE TABLE alarm_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    device_id INT COMMENT '设备ID',
    rule_id INT COMMENT '规则ID',
    alarm_level ENUM('提醒', '警告', '危险') NOT NULL COMMENT '预警级别',
    threshold_value DECIMAL(10,2) COMMENT '阈值数值',
    actual_value DECIMAL(10,2) COMMENT '实际数值',
    message VARCHAR(500) COMMENT '预警消息',
    is_resolved TINYINT DEFAULT 0 COMMENT '是否已解决：1-已解决 0-未解决',
    resolved_at TIMESTAMP NULL COMMENT '解决时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_device (device_id),
    INDEX idx_level (alarm_level),
    INDEX idx_resolved (is_resolved),
    INDEX idx_time (created_at)
) COMMENT '预警记录表';

-- 控制设备表
CREATE TABLE control_devices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_name VARCHAR(100) NOT NULL COMMENT '设备名称',
    device_type VARCHAR(50) NOT NULL COMMENT '设备类型',
    location VARCHAR(200) COMMENT '安装位置',
    status TINYINT DEFAULT 0 COMMENT '状态：1-开启 0-关闭',
    mqtt_topic VARCHAR(200) COMMENT 'MQTT主题',
    current_power DECIMAL(5,2) COMMENT '当前功率(kW)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status)
) COMMENT '控制设备表';

-- 设备控制记录表
CREATE TABLE control_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    device_id INT NOT NULL COMMENT '控制设备ID',
    action ENUM('开启', '关闭', '调节') NOT NULL COMMENT '操作类型',
    target_value DECIMAL(10,2) COMMENT '目标数值',
    actual_value DECIMAL(10,2) COMMENT '实际数值',
    operator VARCHAR(50) COMMENT '操作人',
    remark VARCHAR(200) COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES control_devices(id) ON DELETE CASCADE,
    INDEX idx_device (device_id),
    INDEX idx_time (created_at)
) COMMENT '设备控制记录表';

-- 生产记录表（鱼类繁育）
CREATE TABLE production_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    fish_type VARCHAR(100) COMMENT '鱼类品种',
    quantity DECIMAL(10,2) COMMENT '数量',
    spawn_date DATE COMMENT '产卵日期',
    hatch_date DATE COMMENT '孵化日期',
    growth_stage VARCHAR(50) COMMENT '生长阶段',
    weight DECIMAL(10,2) COMMENT '体重(g)',
    length DECIMAL(10,2) COMMENT '体长(cm)',
    feed_amount DECIMAL(10,2) COMMENT '投喂量(kg)',
    remark TEXT COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_fish_type (fish_type),
    INDEX idx_date (spawn_date)
) COMMENT '生产记录表';

-- 备忘提醒表
CREATE TABLE reminders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(200) NOT NULL COMMENT '提醒标题',
    content TEXT COMMENT '提醒内容',
    reminder_time DATETIME NOT NULL COMMENT '提醒时间',
    is_completed TINYINT DEFAULT 0 COMMENT '是否完成：1-完成 0-未完成',
    completed_at TIMESTAMP NULL COMMENT '完成时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_time (reminder_time),
    INDEX idx_completed (is_completed)
) COMMENT '备忘提醒表';

-- 用户表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    real_name VARCHAR(50) COMMENT '真实姓名',
    role ENUM('admin', 'operator') DEFAULT 'operator' COMMENT '角色：admin-管理员，operator-操作员',
    is_active TINYINT DEFAULT 1 COMMENT '是否启用：1-启用 0-禁用',
    last_login TIMESTAMP NULL COMMENT '最后登录时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '用户表';

-- 用户权限表（预留）
CREATE TABLE user_permissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL COMMENT '用户ID',
    permission VARCHAR(100) COMMENT '权限标识',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
) COMMENT '用户权限表';

-- 添加初始管理员用户（密码：admin123）
-- 注意：实际使用时应该通过应用后台创建
INSERT INTO users (username, password_hash, real_name, role) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYcL.9T6mHm', '系统管理员', 'admin');

-- 数据备份表（存储备份记录）
CREATE TABLE backups (
    id INT PRIMARY KEY AUTO_INCREMENT,
    backup_type VARCHAR(50) NOT NULL COMMENT '备份类型：database/complete',
    file_name VARCHAR(255) COMMENT '文件名',
    file_path VARCHAR(500) COMMENT '文件路径',
    file_size BIGINT COMMENT '文件大小(字节)',
    backup_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '备份时间',
    is_deleted TINYINT DEFAULT 0 COMMENT '是否已删除：1-已删除 0-未删除',
    remark VARCHAR(200) COMMENT '备注',
    INDEX idx_time (backup_time)
) COMMENT '备份记录表';

-- 插入默认预警规则
INSERT INTO alarm_rules (rule_name, sensor_type, threshold_type, threshold_value, level, is_enabled) VALUES
-- 水温规则
('水温过低提醒', 'temperature', 'min', 21, '提醒', 1),
('水温过低警告', 'temperature', 'min', 18, '警告', 1),
('水温过高提醒', 'temperature', 'max', 30, '提醒', 1),
('水温过高警告', 'temperature', 'max', 32, '警告', 1),
('水温过高危险', 'temperature', 'max', 32, '危险', 1),

-- PH值规则
('PH值过低提醒', 'ph', 'min', 5.5, '提醒', 1),
('PH值过低警告', 'ph', 'min', 5, '警告', 1),
('PH值过低危险', 'ph', 'min', 5, '危险', 1),
('PH值过高提醒', 'ph', 'max', 7.5, '提醒', 1),
('PH值过高警告', 'ph', 'max', 8, '警告', 1),
('PH值过高危险', 'ph', 'max', 8, 'danger', 1);

-- 添加默认备忘提醒
INSERT INTO reminders (title, content, reminder_time) VALUES
('每日巡检提醒', '检查设备运行状态、清理传感器、记录养殖数据', DATE_ADD(NOW(), INTERVAL 1 DAY));

COMMIT;
