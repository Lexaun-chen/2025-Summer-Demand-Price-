import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
import os
from datetime import datetime, timedelta
from tqdm import tqdm
import time

# 创建保存文件的目录
output_dir = "./Daily_Adjusting_Factor/"
os.makedirs(output_dir, exist_ok=True)

# 创建到jydb数据库的连接
engine = create_engine("mysql://lexuan_chen%40public%23Thetis:OWFF4UT!@192.168.55.161:2883/jydb")

# 获取所有复权因子数据
sql = '''
SELECT 
    a.InnerCode, 
    a.ExDiviDate, 
    a.RatioAdjustingFactor as AdjustingFactor,
    b.SecuCode AS security_code
FROM 
    jydb.DZ_AdjustingFactor a 
LEFT JOIN 
     smartquant.ReturnDaily b ON a.InnerCode = b.InnerCode

'''

# 执行查询
with engine.connect() as conn:
    print("正在获取复权因子数据...")
    df_adj = pd.read_sql(text(sql), conn)
    
    # 获取交易日历
    print("正在获取交易日历...")
    trading_days = pd.read_sql(text('''
        SELECT DISTINCT TradingDay 
        FROM jydb.QT_TradingDayNew 
        WHERE IfTradingDay=1 
        AND TradingDay <= '2025-06-23'
        ORDER BY TradingDay
    '''), conn)

print(f"获取到 {len(df_adj)} 条复权因子记录")
print(f"获取到 {len(trading_days)} 个交易日")

# 转换日期格式
df_adj['ExDiviDate'] = pd.to_datetime(df_adj['ExDiviDate'])
trading_days['TradingDay'] = pd.to_datetime(trading_days['TradingDay'])

# 为每个交易日创建复权因子文件
for day in tqdm(trading_days['TradingDay']):
    # 筛选出该日期之前的最新复权因子
    df_day = df_adj[df_adj['ExDiviDate'] <= day].copy()
    
    if len(df_day) > 0:
        # 对每个股票取最近的复权因子
        df_day = df_day.sort_values(['InnerCode', 'ExDiviDate'])
        df_latest = df_day.groupby('InnerCode').last().reset_index()
        
        # 保存为parquet文件
        file_name = day.strftime("%Y%m%d") + ".parquet"
        file_path = os.path.join(output_dir, file_name)
        df_latest.to_parquet(file_path, index=False)
    
    # 避免过度占用数据库资源，每处理10个日期暂停一下
    if day.day % 10 == 0:
        time.sleep(1)

print("所有日期的复权因子文件已创建完成！")
