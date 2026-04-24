/// 应用配置常量
/// 所有硬编码的配置值应在此文件管理

class AppConfig {
  // API 默认地址（首次安装时使用）
  // 用户修改后会自动保存到本地存储
  static const String defaultApiUrl = 'http://192.168.1.200:8080';
  
  // WebSocket 默认路径
  static const String wsPath = '/ws';
  
  // API 超时设置（毫秒）
  static const int connectTimeout = 30000;
  static const int receiveTimeout = 30000;
  static const int sendTimeout = 30000;
  
  // 本地存储 Key
  static const String keyApiUrl = 'api_url';
  static const String keyClientId = 'client_id';
  static const String keyAutoRefresh = 'auto_refresh';
  static const String keyRefreshInterval = 'refresh_interval';
  static const String keyNotifications = 'notifications_enabled';
  static const String keyDarkMode = 'dark_mode';
}
