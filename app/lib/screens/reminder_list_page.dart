import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:fishfarm_monitor/models/reminder.dart';
import 'package:fishfarm_monitor/services/api_service.dart';

class ReminderListPage extends StatefulWidget {
  const ReminderListPage({super.key});

  @override
  State<ReminderListPage> createState() => _ReminderListPageState();
}

class _ReminderListPageState extends State<ReminderListPage> {
  final ApiService _apiService = ApiService();
  List<Reminder> _reminders = [];
  bool _isLoading = true;
  int _filterStatus = 0; // 0-全部, 1-未完成, 2-已完成

  @override
  void initState() {
    super.initState();
    _loadReminders();
  }

  Future<void> _loadReminders() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final reminders = await _apiService.getReminders(isCompleted: _filterStatus == 2 ? 1 : -1);
      setState(() {
        _reminders = reminders;
        _isLoading = false;
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('加载提醒失败: $e')),
        );
      }
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _deleteReminder(int id) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认删除'),
        content: const Text('确定要删除这条提醒吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('删除'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        await _apiService.deleteReminder(id);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('提醒已删除')),
          );
          _loadReminders();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('删除失败: $e')),
          );
        }
      }
    }
  }

  Future<void> _toggleComplete(int id, bool currentStatus) async {
    try {
      final success = await _apiService.markReminderCompleted(id);
      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(currentStatus ? '已标记为未完成' : '已标记为完成')),
        );
        _loadReminders();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('操作失败: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('提醒管理'),
        backgroundColor: Colors.blue[700],
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadReminders,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                _buildFilterBar(),
                Expanded(
                  child: _reminders.isEmpty
                      ? _buildEmptyState()
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _reminders.length,
                          itemBuilder: (context, index) {
                            return _buildReminderCard(_reminders[index]);
                          },
                        ),
                ),
              ],
            ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddReminderDialog(),
        icon: const Icon(Icons.add),
        label: const Text('添加提醒'),
      ),
    );
  }

  Widget _buildFilterBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.2),
            spreadRadius: 1,
            blurRadius: 3,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          const Text('筛选: '),
          const SizedBox(width: 8),
          _buildFilterChip('全部', 0, Icons.groups),
          const SizedBox(width: 8),
          _buildFilterChip('未完成', 1, Icons.task_alt),
          const SizedBox(width: 8),
          _buildFilterChip('已完成', 2, Icons.check_circle),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String label, int status, IconData icon) {
    final isSelected = _filterStatus == status;
    return FilterChip(
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16),
          const SizedBox(width: 4),
          Text(label),
        ],
      ),
      selected: isSelected,
      onSelected: (_) {
        setState(() {
          _filterStatus = status;
        });
        _loadReminders();
      },
      backgroundColor: Colors.white,
      selectedColor: Colors.blue[700],
      checkmarkColor: Colors.white,
    );
  }

  Widget _buildReminderCard(Reminder reminder) {
    final isCompleted = reminder.isCompleted;
    final formattedTime = DateFormat('yyyy-MM-dd HH:mm').format(
      DateTime.parse(reminder.reminderTime),
    );

    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => _showEditReminderDialog(reminder),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      reminder.title,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: isCompleted ? Colors.grey : Colors.black87,
                        decoration: isCompleted
                            ? TextDecoration.lineThrough
                            : TextDecoration.none,
                      ),
                    ),
                  ),
                  Switch(
                    value: isCompleted,
                     onChanged: (value) => _toggleComplete(reminder.id!, value),
                    activeColor: Colors.blue[700],
                  ),
                ],
              ),
              if (reminder.content != null && reminder.content!.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(
                  reminder.content!,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
              ],
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(
                    Icons.access_time,
                    size: 16,
                    color: Colors.grey[600],
                  ),
                  const SizedBox(width: 4),
                  Text(
                    formattedTime,
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.grey[600],
                    ),
                  ),
                  const Spacer(),
                  IconButton(
                    icon: const Icon(Icons.edit, size: 20),
                    onPressed: () => _showEditReminderDialog(reminder),
                    color: Colors.blue[700],
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete, size: 20),
                    onPressed: () => _deleteReminder(reminder.id!),
                    color: Colors.red,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            _filterStatus == 2 ? Icons.check_circle_outline : Icons.inbox_outlined,
            size: 80,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            _filterStatus == 2 ? '没有已完成的提醒' : '没有提醒记录',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '点击下方按钮添加新提醒',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  void _showAddReminderDialog() {
    final titleController = TextEditingController();
    final contentController = TextEditingController();
    final timeController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('添加提醒'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              TextField(
                controller: titleController,
                decoration: const InputDecoration(
                  labelText: '标题',
                  hintText: '请输入提醒标题',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: contentController,
                decoration: const InputDecoration(
                  labelText: '内容',
                  hintText: '请输入提醒内容（可选）',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: timeController,
                decoration: const InputDecoration(
                  labelText: '提醒时间',
                  hintText: '选择提醒时间',
                  border: OutlineInputBorder(),
                ),
                onTap: () async {
                  final DateTime? picked = await showDatePicker(
                    context: context,
                    initialDate: DateTime.now(),
                    firstDate: DateTime.now(),
                    lastDate: DateTime.now().add(const Duration(days: 365)),
                  );
                  if (picked != null) {
                    final TimeOfDay? time = await showTimePicker(
                      context: context,
                      initialTime: TimeOfDay.now(),
                    );
                    if (time != null) {
                      final DateTime selectedDateTime = DateTime(
                        picked.year,
                        picked.month,
                        picked.day,
                        time.hour,
                        time.minute,
                      );
                      timeController.text = selectedDateTime.toIso8601String();
                    }
                  }
                },
                readOnly: true,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () async {
              final title = titleController.text.trim();
              if (title.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('请输入提醒标题')),
                );
                return;
              }

              final content = contentController.text.trim();
              final reminderTime = timeController.text.isEmpty
                  ? null
                  : timeController.text.trim();

              try {
                await _apiService.createReminder(
                  title: title,
                  content: content.isEmpty ? null : content,
                  reminderTime: reminderTime,
                );
                if (mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('提醒添加成功')),
                  );
                  _loadReminders();
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('添加失败: $e')),
                  );
                }
              }
            },
            child: const Text('添加'),
          ),
        ],
      ),
    );
  }

  void _showEditReminderDialog(Reminder reminder) {
    final titleController = TextEditingController(text: reminder.title);
    final contentController = TextEditingController(text: reminder.content);
    final timeController = TextEditingController(text: reminder.reminderTime);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('编辑提醒'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              TextField(
                controller: titleController,
                decoration: const InputDecoration(
                  labelText: '标题',
                  hintText: '请输入提醒标题',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: contentController,
                decoration: const InputDecoration(
                  labelText: '内容',
                  hintText: '请输入提醒内容（可选）',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 16),
              TextField(
                controller: timeController,
                decoration: const InputDecoration(
                  labelText: '提醒时间',
                  hintText: '选择提醒时间',
                  border: OutlineInputBorder(),
                ),
                onTap: () async {
                  final DateTime? picked = await showDatePicker(
                    context: context,
                    initialDate: DateTime.now(),
                    firstDate: DateTime.now(),
                    lastDate: DateTime.now().add(const Duration(days: 365)),
                  );
                  if (picked != null) {
                    final TimeOfDay? time = await showTimePicker(
                      context: context,
                      initialTime: TimeOfDay.now(),
                    );
                    if (time != null) {
                      final DateTime selectedDateTime = DateTime(
                        picked.year,
                        picked.month,
                        picked.day,
                        time.hour,
                        time.minute,
                      );
                      timeController.text = selectedDateTime.toIso8601String();
                    }
                  }
                },
                readOnly: true,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () async {
              final title = titleController.text.trim();
              if (title.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('请输入提醒标题')),
                );
                return;
              }

              final content = contentController.text.trim();
              final reminderTime = timeController.text.isEmpty
                  ? null
                  : timeController.text.trim();

              try {
                await _apiService.updateReminder(
                  id: reminder.id!,
                  title: title,
                  content: content.isEmpty ? null : content,
                  reminderTime: reminderTime,
                );
                if (mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('提醒更新成功')),
                  );
                  _loadReminders();
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('更新失败: $e')),
                  );
                }
              }
            },
            child: const Text('保存'),
          ),
        ],
      ),
    );
  }
}
