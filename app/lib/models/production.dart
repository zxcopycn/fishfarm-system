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
      id: json['id'],
      fishType: json['fish_type'],
      quantity: json['quantity'].toDouble(),
      spawnDate: DateTime.parse(json['spawn_date']),
      hatchDate: json['hatch_date'] != null
          ? DateTime.parse(json['hatch_date'])
          : null,
      growthStage: json['growth_stage'],
      weight: json['weight'].toDouble(),
      length: json['length'].toDouble(),
      feedAmount: json['feed_amount'].toDouble(),
      remark: json['remark'],
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
