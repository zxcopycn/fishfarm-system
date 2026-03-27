import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import 'package:fishfarm_monitor/models/device.dart';
import 'package:fishfarm_monitor/models/sensor_data.dart';
import 'package:fishfarm_monitor/services/api_service.dart';

class HistoryPage extends StatefulWidget {
  const HistoryPage({super.key});

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  bool _isLoading = true;
  List<Device> _devices = [];
  Device? _selectedDevice;
  List<SensorData> _sensorData = [];
  String _selectedType = 'temperature'; // temperature, ph, ammonia, nitrite, oxygen

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final devices = await ApiService().getDevices();
      setState(() {
        _devices = devices;
        if (_selectedDevice == null && devices.isNotEmpty) {
          _selectedDevice = devices.first;
        }
      });

      if (_selectedDevice != null) {
        await _loadHistoricalData();
      }

      setState(() => _isLoading = false);
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载数据失败: $e')),
        );
      }
    }
  }

  Future<void> _loadHistoricalData() async {
    if (_selectedDevice == null) return;

    try {
      final startTime = DateTime.now().subtract(const Duration(hours: 24));
      final data = await ApiService().getHistoricalSensorData(
        deviceId: _selectedDevice!.id,
        startTime: startTime,
        limit: 100,
      );

      setState(() => _sensorData = data);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载历史数据失败: $e')),
        );
      }
    }
  }

  String _getTypeName(String type) {
    switch (type) {
      case 'temperature':
        return '温度';
      case 'ph':
        return 'PH值';
      case 'ammonia':
        return '氨氮';
      case 'nitrite':
        return '亚盐';
      case 'oxygen':
        return '溶氧';
      default:
        return type;
    }
  }

  String _getTypeUnit(String type) {
    switch (type) {
      case 'temperature':
        return '℃';
      case 'ammonia':
      case 'nitrite':
      case 'oxygen':
        return 'mg/L';
      default:
        return '';
    }
  }

  double? _getValue(SensorData data, String type) {
    switch (type) {
      case 'temperature':
        return data.temperature;
      case 'ph':
        return data.ph;
      case 'ammonia':
        return data.ammonia;
      case 'nitrite':
        return data.nitrite;
      case 'oxygen':
        return data.oxygen;
      default:
        return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('历史数据'),
        backgroundColor: Colors.blue[700],
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _buildHistory(),
    );
  }

  Widget _buildHistory() {
    return Column(
      children: [
        // 设备选择器
        _buildDeviceSelector(),
        // 类型选择器
        _buildTypeSelector(),
        // 图表
        Expanded(
          child: _buildChart(),
        ),
      ],
    );
  }

  Widget _buildDeviceSelector() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: DropdownButtonFormField<Device>(
        value: _selectedDevice,
        decoration: const InputDecoration(
          labelText: '选择设备',
          prefixIcon: Icon(Icons.devices),
          border: OutlineInputBorder(),
        ),
        items: _devices.map((device) {
          return DropdownMenuItem(
            value: device,
            child: Text(device.deviceName),
          );
        }).toList(),
        onChanged: (device) {
          setState(() {
            _selectedDevice = device;
            _sensorData.clear();
          });
          _loadHistoricalData();
        },
      );
    }
  }

  Widget _buildTypeSelector() {
    final types = [
      {'value': 'temperature', 'label': '温度'},
      {'value': 'ph', 'label': 'PH值'},
      {'value': 'ammonia', 'label': '氨氮'},
      {'value': 'nitrite', 'label': '亚盐'},
      {'value': 'oxygen', 'label': '溶氧'},
    ];

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: types.map((type) {
            final isSelected = _selectedType == type['value'];
            return Padding(
              padding: const EdgeInsets.only(right: 8),
              child: ChoiceChip(
                label: Text(type['label'] as String),
                selected: isSelected,
                onSelected: (selected) {
                  if (selected) {
                    setState(() => _selectedType = type['value'] as String);
                  }
                },
                selectedColor: Colors.blue[700],
                backgroundColor: Colors.grey[200],
                labelStyle: TextStyle(
                  color: isSelected ? Colors.white : Colors.black,
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildChart() {
    if (_sensorData.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.show_chart, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            const Text(
              '暂无历史数据',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
          ],
        ),
      );
    }

    // 过滤有效数据
    final validData = _sensorData
        .map((data) => {
              'value': _getValue(data, _selectedType),
              'time': data.createdAt,
            })
        .where((item) => item['value'] != null)
        .toList();

    if (validData.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.info, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            const Text(
              '暂无该类型数据',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${_getTypeName(_selectedType)}趋势图',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    '最近24小时',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Expanded(
                child: LineChart(
                  LineChartData(
                    gridData: FlGridData(
                      show: true,
                      drawVerticalLine: false,
                      horizontalInterval: 1,
                    ),
                    titlesData: FlTitlesData(
                      show: true,
                      bottomTitles: AxisTitles(
                        sideTitles: SideTitles(
                          showTitles: true,
                          getTitlesWidget: (value, meta) {
                            if (value.toInt() % 5 == 0) {
                              final index = value.toInt();
                              if (index < validData.length) {
                                final time = validData[index]['time'] as DateTime;
                                return Text(
                                  DateFormat('HH:mm').format(time),
                                  style: const TextStyle(fontSize: 10),
                                );
                              }
                            }
                            return const Text('');
                          },
                          reservedSize: 30,
                        ),
                      ),
                      leftTitles: AxisTitles(
                        sideTitles: SideTitles(
                          showTitles: true,
                          getTitlesWidget: (value, meta) {
                            return Text(
                              value.toStringAsFixed(1),
                              style: const TextStyle(fontSize: 10),
                            );
                          },
                          reservedSize: 40,
                        ),
                      ),
                      topTitles: const AxisTitles(
                        sideTitles: SideTitles(showTitles: false),
                      ),
                      rightTitles: const AxisTitles(
                        sideTitles: SideTitles(showTitles: false),
                      ),
                    ),
                    borderData: FlBorderData(
                      show: true,
                      border: Border.all(color: const Color(0xff37434d)),
                    ),
                    minX: 0,
                    maxX: (validData.length - 1).toDouble(),
                    minY: validData
                            .map((item) => (item['value'] as double))
                            .reduce((a, b) => a < b ? a : b) -
                        1,
                    maxY: validData
                            .map((item) => (item['value'] as double))
                            .reduce((a, b) => a > b ? a : b) +
                        1,
                    lineBarsData: [
                      LineChartBarData(
                        spots: List.generate(validData.length, (index) {
                          return FlSpot(
                            index.toDouble(),
                            validData[index]['value'] as double,
                          );
                        }),
                        isCurved: true,
                        gradient: LinearGradient(
                          colors: [
                            Colors.blue[700]!,
                            Colors.blue[400]!,
                          ],
                        ),
                        barWidth: 3,
                        isStrokeCapRound: true,
                        dotData: FlDotData(show: false),
                        belowBarData: BarAreaData(
                          show: true,
                          gradient: LinearGradient(
                            colors: [
                              Colors.blue[700]!.withOpacity(0.3),
                              Colors.blue[400]!.withOpacity(0.1),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
