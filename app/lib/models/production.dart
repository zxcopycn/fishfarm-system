import '../../utils/type_converters.dart';

class ProductionRecord {
  final int id;
  final String fishType;
  final double quantity; // 数量（尾/千克）
  final DateTime spawnDate; // 投放日期
  final DateTime? hatchDate; // 孵化日期
  final String growthStage; // 生长阶段
  final double weight; // 平均重量
  final double length; // 平均长度
  final double feedAmount; // 投喂量
  final String? remark;
  final DateTime createdAt; // 创建时间
  final DateTime updatedAt; // 更新时间

  ProductionRecord({
    required this.id,
    required this.fishType,
    required this.quantity,
    required this.spawnDate,
    this.hatchDate,
    required this.growthStage,
    required this.weight,
    required this.length,
    required this.feedAmount,
    this.remark,
    required this.createdAt,
    required this.updatedAt,
  });

  factory ProductionRecord.fromJson(Map<String, dynamic> json) {
    return ProductionRecord(
      id: TypeConverters.safeInt(json['id']) ?? 0,
      fishType: json['fish_type']?.toString() ?? '未知鱼种',
      quantity: TypeConverters.safeDouble(json['quantity']) ?? 0.0,
      spawnDate: TypeConverters.safeDateTime(json['spawn_date']) ?? DateTime.now(),
      hatchDate: TypeConverters.safeDateTime(json['hatch_date']),
      growthStage: json['growth_stage']?.toString() ?? '未知阶段',
      weight: TypeConverters.safeDouble(json['weight']) ?? 0.0,
      length: TypeConverters.safeDouble(json['length']) ?? 0.0,
      feedAmount: TypeConverters.safeDouble(json['feed_amount']) ?? 0.0,
      remark: json['remark']?.toString(),
      createdAt: TypeConverters.safeDateTime(json['created_at']) ?? DateTime.now(),
      updatedAt: TypeConverters.safeDateTime(json['updated_at']) ?? DateTime.now(),
          : DateTime.now(),
    );
  }
}

class ProductionStatistics {
  final String fishType;
  final int totalQuantity;
  final double totalWeight;
  final int totalLength;
  final double totalFeedAmount;
  final int recordCount;

  ProductionStatistics({
    required this.fishType,
    required this.totalQuantity,
    required this.totalWeight,
    required this.totalLength,
    required this.totalFeedAmount,
    required this.recordCount,
  });

  factory ProductionStatistics.fromJson(Map<String, dynamic> json) {
    return ProductionStatistics(
      fishType: json['fish_type'],
      totalQuantity: json['total_quantity'],
      totalWeight: json['total_weight'].toDouble(),
      totalLength: json['total_length'],
      totalFeedAmount: json['total_feed_amount'].toDouble(),
      recordCount: json['record_count'],
    );
  }
}
