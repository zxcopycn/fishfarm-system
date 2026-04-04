#!/usr/bin/env python3
"""
检查和初始化数据库
"""

import sys
import os
import sqlite3

def check_database():
    """检查数据库状态"""
    db_path = "/home/node/.openclaw/workspace/fishfarm-system/backend/fishfarm.db"
    
    if not os.path.exists(db_path):
        print(f"✅ 数据库文件不存在，将创建新数据库: {db_path}")
        return False
    
    print(f"📁 数据库文件已存在: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查有哪些表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📊 已创建的表: {len(tables)}")
        for i, table in enumerate(tables, 1):
            print(f"  {i:2d}. {table[0]}")
        
        # 检查主要表是否存在
        main_tables = ['device_types', 'devices', 'sensor_data', 'users', 'reminders']
        missing_tables = [table for table in main_tables if table not in [t[0] for t in tables]]
        
        if missing_tables:
            print(f"⚠️  缺少表: {missing_tables}")
            return False
        else:
            print("✅ 主要表都已存在")
            return True
            
    except Exception as e:
        print(f"❌ 检查数据库失败: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def create_database():
    """创建数据库表"""
    print("🚀 开始创建数据库表...")
    
    try:
        from app.database import Base, engine
        
        # 创建所有表，忽略已存在的对象
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        print("✅ 数据库表创建完成！")
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库表失败: {e}")
        return False

def main():
    print("=" * 60)
    print("数据库检查和初始化")
    print("=" * 60)
    
    if not check_database():
        print("\n" + "=" * 60)
        print("创建数据库表...")
        if create_database():
            print("\n" + "=" * 60)
            print("🎉 数据库初始化成功！")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ 数据库初始化失败！")
            print("=" * 60)
            return False
    else:
        print("\n" + "=" * 60)
        print("🎉 数据库已就绪！")
        print("=" * 60)
    
    print(f"\n数据库位置: /home/node/.openclaw/workspace/fishfarm-system/backend/fishfarm.db")
    print("🚀 渔场系统已准备就绪！")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)