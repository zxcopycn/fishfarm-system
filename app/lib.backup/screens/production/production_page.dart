import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:fishfarm_monitor/models/production.dart';
import 'package:fishfarm_monitor/services/api_service.dart';

class ProductionPage extends StatefulWidget {
  const ProductionPage({super.key});

  @override
  State<ProductionPage> createState() => _ProductionPageState();
}

class _ProductionPageState extends State<ProductionPage> {
  bool _isLoading = true;
  List<ProductionRecord> _records = [];
  String _filterFishType = 'all';

  @override
  void initState() {
    super.initState();
    _loadRecords();
  }

  Future<void> _loadRecords() async {
    try {
      String? fishType;
      if (_filterFishType != 'all') {
        fishType = _filterFishType;
      }

      final records = await ApiService().getProductionRecords(
        fishType: fishType,
        limit: 50,
      );

      setState(() {
        _records = records;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载生产记录失败: $e')),
        );
      }
    }
  }

  void _showAddDialog() {
    final _formKey = GlobalKey<FormState>();
    final _fishTypeController = TextEditingController();
    final _quantityController = TextEditingController(text: '0');
    final _weightController = TextEditingController(text: '0');
    final _lengthController = TextEditingController(text: '0');
    final _feedAmountController = TextEditingController(text: '0');
    DateTime? _spawnDate;
    DateTime? _hatchDate;
    String? _growthStage;
    final _remarkController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('添加生产记录'),
          content: SizedBox(
            width: 500,
            child: SingleChildScrollView(
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    TextFormField(
                      controller: _fishTypeController,
                      decoration: const InputDecoration(
                        labelText: '鱼类品种 *',
                        hintText: '例如：鲈鱼、鲤鱼',
                        border: OutlineInputBorder(),
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return '请输入鱼类品种';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _quantityController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: '数量 (尾)',
                        border: OutlineInputBorder(),
                        prefixText: '数量: ',
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return '请输入数量';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _weightController,
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      decoration: const InputDecoration(
                        labelText: '平均体重',
                        border: OutlineInputBorder(),
                        prefixText: '体重: ',
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _lengthController,
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      decoration: const InputDecoration(
                        labelText: '平均体长',
                        border: OutlineInputBorder(),
                        prefixText: '体长: ',
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _feedAmountController,
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      decoration: const InputDecoration(
                        labelText: '投喂量',
                        border: OutlineInputBorder(),
                        prefixText: '投喂量: ',
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: ListTile(
                            title: const Text('投喂日期'),
                            subtitle: _spawnDate != null
                                ? Text(DateFormat('yyyy-MM-dd').format(_spawnDate!))
                                : null,
                            onTap: () async {
                              final date = await showDatePicker(
                                context: context,
                                initialDate: DateTime.now(),
                                firstDate: DateTime(2000),
                                lastDate: DateTime(2100),
                              );
                              if (date != null) {
                                setDialogState(() => _spawnDate = date);
                              }
                            },
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: ListTile(
                            title: const Text('孵化日期'),
                            subtitle: _hatchDate != null
                                ? Text(DateFormat('yyyy-MM-dd').format(_hatchDate!))
                                : null,
                            onTap: () async {
                              final date = await showDatePicker(
                                context: context,
                                initialDate: DateTime.now(),
                                firstDate: DateTime(2000),
                                lastDate: DateTime(2100),
                              );
                              if (date != null) {
                                setDialogState(() => _hatchDate = date);
                              }
                            },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<String>(
                      decoration: const InputDecoration(
                        labelText: '生长阶段',
                        border: OutlineInputBorder(),
                      ),
                      value: _growthStage,
                      items: const [
                        DropdownMenuItem(
                          value: '苗种期',
                          child: Text('苗种期'),
                        ),
                        DropdownMenuItem(
                          value: '生长期',
                          child: Text('生长期'),
                        ),
                        DropdownMenuItem(
                          value: '育肥期',
                          child: Text('育肥期'),
                        ),
                        DropdownMenuItem(
                          value: '成熟期',
                          child: Text('成熟期'),
                        ),
                      ],
                      onChanged: (value) {
                        setDialogState(() => _growthStage = value);
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _remarkController,
                      decoration: const InputDecoration(
                        labelText: '备注',
                        border: OutlineInputBorder(),
                      ),
                      maxLines: 3,
                    ),
                  ],
                ),
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('取消'),
            ),
            ElevatedButton(
              onPressed: () async {
                if (_formKey.currentState!.validate()) {
                  try {
                    await ApiService().createProductionRecord(
                      fishType: _fishTypeController.text.trim(),
                      quantity: double.tryParse(_quantityController.text) ?? 0,
                      weight: double.tryParse(_weightController.text),
                      length: double.tryParse(_lengthController.text),
                      feedAmount: double.tryParse(_feedAmountController.text),
                      spawnDate: _spawnDate,
                      hatchDate: _hatchDate,
                      growthStage: _growthStage,
                      remark: _remarkController.text.trim().isEmpty ? null : _remarkController.text.trim(),
                    );

                    if (mounted) {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('生产记录添加成功！'),
                          backgroundColor: Colors.green,
                        ),
                      );
                      _loadRecords();
                    }
                  } catch (e) {
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('添加失败: $e'),
                          backgroundColor: Colors.red,
                        ),
                      );
                    }
                  }
                }
              },
              child: const Text('添加'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('生产记录'),
        backgroundColor: Colors.blue[700],
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadRecords,
          ),
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: _showAddDialog,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                _buildFilters(),
                Expanded(
                  child: _buildRecordList(),
                ),
              ],
            ),
    );
  }

  Widget _buildFilters() {
    // 提取所有鱼类品种
    final fishTypes = _records
        .map((r) => r.fishType)
        .where((type) => type != null && type.isNotEmpty)
        .toSet()
        .toList()
      ..sort();

    return Container(
      padding: const EdgeInsets.all(16),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            _buildFilterChip('all', '全部'),
            if (fishTypes.isNotEmpty) ...[
              const SizedBox(width: 8),
              ...fishTypes.map((type) {
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: _buildFilterChip(type, type!),
                );
              }).toList(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildFilterChip(String fishType, String label) {
    final isSelected = _filterFishType == fishType;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          _filterFishType = fishType;
        });
        _loadRecords();
      },
      selectedColor: Colors.blue[700],
      checkmarkColor: Colors.white,
      backgroundColor: Colors.grey[200],
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : Colors.black,
      ),
    );
  }

  Widget _buildRecordList() {
    if (_records.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.agriculture, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            const Text(
              '暂无生产记录',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _showAddDialog,
              icon: const Icon(Icons.add),
              label: const Text('添加记录'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _loadRecords,
      child: ListView.builder(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: _records.length,
        itemBuilder: (context, index) {
          final record = _records[index];
          return _buildRecordCard(record);
        },
      ),
    );
  }

  Widget _buildRecordCard(ProductionRecord record) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        children: [
          InkWell(
            onTap: () {
              _showEditDialog(record);
            },
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(
                        Icons.set_meal,
                        size: 32,
                        color: Colors.blue,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              record.fishType,
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            if (record.growthStage.isNotEmpty)
                              Text(
                                record.growthStage,
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey[600],
                                ),
                              ),
                          ],
                        ),
                      ),
                      Row(
                        children: [
                          IconButton(
                            icon: const Icon(Icons.edit, size: 20),
                            onPressed: () => _showEditDialog(record),
                            tooltip: '编辑',
                          ),
                          IconButton(
                            icon: const Icon(Icons.delete, size: 20, color: Colors.red),
                            onPressed: () => _deleteRecord(record),
                            tooltip: '删除',
                          ),
                        ],
                      ),
                    ],
                  ),
                  const Divider(),
                  if (record.quantity > 0) ...[
                    _buildInfoRow(
                      Icons.straighten,
                      '数量',
                      '${record.quantity} 尾',
                    ),
                  ],
                  if (record.weight > 0) ...[
                    _buildInfoRow(
                      Icons.scale,
                      '体重',
                      '${record.weight} g',
                    ),
                  ],
                  if (record.length > 0) ...[
                    _buildInfoRow(
                      Icons.height,
                      '体长',
                      '${record.length} cm',
                    ),
                  ],
                  if (record.feedAmount > 0) ...[
                    _buildInfoRow(
                      Icons.restaurant,
                      '投喂量',
                      '${record.feedAmount} kg',
                    ),
                  ],
                  if (record.spawnDate.year > 2000) ...[
                    _buildInfoRow(
                      Icons.cake,
                      '投喂日期',
                      DateFormat('yyyy-MM-dd').format(record.spawnDate),
                    ),
                  ],
                  if (record.hatchDate != null && record.hatchDate!.year > 2000) ...[
                    _buildInfoRow(
                      Icons.child_care,
                      '孵化日期',
                      DateFormat('yyyy-MM-dd').format(record.hatchDate!),
                    ),
                  ],
                  if (record.remark != null && record.remark!.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Text(
                      '备注: ${record.remark}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[500],
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ],
                  if (record.createdAt.year > 2000) ...[
                    const SizedBox(height: 8),
                    Text(
                      '创建于: ${DateFormat('yyyy-MM-dd HH:mm').format(record.createdAt)}',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[500],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _deleteRecord(ProductionRecord record) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认删除'),
        content: Text('确定要删除这条生产记录吗？此操作不可恢复。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () async {
              try {
                await ApiService().deleteProductionRecord(record.id);

                if (mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('删除成功！'),
                      backgroundColor: Colors.green,
                    ),
                  );
                  _loadRecords();
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('删除失败: $e'),
                      backgroundColor: Colors.red,
                    ),
                  );
                }
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('删除'),
          ),
        ],
      ),
    );
  }

  void _showEditDialog(ProductionRecord record) {
    final _formKey = GlobalKey<FormState>();
    final _fishTypeController = TextEditingController(text: record.fishType);
    final _quantityController = TextEditingController(text: record.quantity.toString());
    final _weightController = TextEditingController(text: record.weight > 0 ? record.weight.toString() : '');
    final _lengthController = TextEditingController(text: record.length > 0 ? record.length.toString() : '');
    final _feedAmountController = TextEditingController(text: record.feedAmount > 0 ? record.feedAmount.toString() : '');
    DateTime? _spawnDate = record.spawnDate;
    DateTime? _hatchDate = record.hatchDate;
    String? _growthStage = record.growthStage;
    final _remarkController = TextEditingController(text: record.remark ?? '');

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('编辑生产记录'),
          content: SizedBox(
            width: 500,
            child: SingleChildScrollView(
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    TextFormField(
                      controller: _fishTypeController,
                      decoration: const InputDecoration(
                        labelText: '鱼类品种 *',
                        hintText: '例如：鲈鱼、鲤鱼',
                        border: OutlineInputBorder(),
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return '请输入鱼类品种';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _quantityController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: '数量 (尾)',
                        border: OutlineInputBorder(),
                        prefixText: '数量: ',
                      ),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return '请输入数量';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _weightController,
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      decoration: const InputDecoration(
                        labelText: '平均体重',
                        border: OutlineInputBorder(),
                        prefixText: '体重: ',
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _lengthController,
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      decoration: const InputDecoration(
                        labelText: '平均体长',
                        border: OutlineInputBorder(),
                        prefixText: '体长: ',
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _feedAmountController,
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      decoration: const InputDecoration(
                        labelText: '投喂量',
                        border: OutlineInputBorder(),
                        prefixText: '投喂量: ',
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: ListTile(
                            title: const Text('投喂日期'),
                            subtitle: _spawnDate != null
                                ? Text(DateFormat('yyyy-MM-dd').format(_spawnDate!))
                                : null,
                            onTap: () async {
                              final date = await showDatePicker(
                                context: context,
                                initialDate: DateTime.now(),
                                firstDate: DateTime(2000),
                                lastDate: DateTime(2100),
                              );
                              if (date != null) {
                                setDialogState(() => _spawnDate = date);
                              }
                            },
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: ListTile(
                            title: const Text('孵化日期'),
                            subtitle: _hatchDate != null
                                ? Text(DateFormat('yyyy-MM-dd').format(_hatchDate!))
                                : null,
                            onTap: () async {
                              final date = await showDatePicker(
                                context: context,
                                initialDate: DateTime.now(),
                                firstDate: DateTime(2000),
                                lastDate: DateTime(2100),
                              );
                              if (date != null) {
                                setDialogState(() => _hatchDate = date);
                              }
                            },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<String>(
                      decoration: const InputDecoration(
                        labelText: '生长阶段',
                        border: OutlineInputBorder(),
                      ),
                      value: _growthStage,
                      items: const [
                        DropdownMenuItem(
                          value: '苗种期',
                          child: Text('苗种期'),
                        ),
                        DropdownMenuItem(
                          value: '生长期',
                          child: Text('生长期'),
                        ),
                        DropdownMenuItem(
                          value: '育肥期',
                          child: Text('育肥期'),
                        ),
                        DropdownMenuItem(
                          value: '成熟期',
                          child: Text('成熟期'),
                        ),
                      ],
                      onChanged: (value) {
                        setDialogState(() => _growthStage = value);
                      },
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _remarkController,
                      decoration: const InputDecoration(
                        labelText: '备注',
                        border: OutlineInputBorder(),
                      ),
                      maxLines: 3,
                    ),
                  ],
                ),
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('取消'),
            ),
            ElevatedButton(
              onPressed: () async {
                if (_formKey.currentState!.validate()) {
                  try {
                    await ApiService().updateProductionRecord(
                      record.id,
                      fishType: _fishTypeController.text.trim(),
                      quantity: double.tryParse(_quantityController.text) ?? 0,
                      weight: double.tryParse(_weightController.text),
                      length: double.tryParse(_lengthController.text),
                      feedAmount: double.tryParse(_feedAmountController.text),
                      spawnDate: _spawnDate,
                      hatchDate: _hatchDate,
                      growthStage: _growthStage,
                      remark: _remarkController.text.trim().isEmpty ? null : _remarkController.text.trim(),
                    );

                    if (mounted) {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('生产记录更新成功！'),
                          backgroundColor: Colors.green,
                        ),
                      );
                      _loadRecords();
                    }
                  } catch (e) {
                    if (mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('更新失败: $e'),
                          backgroundColor: Colors.red,
                        ),
                      );
                    }
                  }
                }
              },
              child: const Text('保存'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 16, color: Colors.grey[600]),
          const SizedBox(width: 8),
          Text(
            '$label: ',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[600],
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
