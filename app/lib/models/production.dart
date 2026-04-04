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
      id: json['id'] as int? ?? 0,
      fishType: json['fish_type'] as String? ?? '未知鱼种',
      quantity: (json['quantity'] as num?)?.toDouble() ?? 0.0,
      spawnDate: json['spawn_date'] != null
          ? DateTime.parse(json['spawn_date'])
          : DateTime.now(),
      hatchDate: json['hatch_date'] != null
          ? DateTime.parse(json['hatch_date'])
          : null,
      growthStage: json['growth_stage'] as String? ?? '未知阶段',
      weight: (json['weight'] as num?)?.toDouble() ?? 0.0,
      length: (json['length'] as num?)?.toDouble() ?? 0.0,
      feedAmount: (json['feed_amount'] as num?)?.toDouble() ?? 0.0,
      remark: json['remark'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : DateTime.now(),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
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
