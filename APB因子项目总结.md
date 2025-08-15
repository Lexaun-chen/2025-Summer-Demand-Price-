### Stage One：研报复现与简单改进
[20210722-东方证券-因子选股系列之七十六\_基于委托订单数据的alpha因子\_17页\_2mb.pdf](/jiawei.tang/order_apb/uploads/98d16872081f43e876611b4434a86cba/20210722-%E4%B8%9C%E6%96%B9%E8%AF%81%E5%88%B8-%E5%9B%A0%E5%AD%90%E9%80%89%E8%82%A1%E7%B3%BB%E5%88%97%E4%B9%8B%E4%B8%83%E5%8D%81%E5%85%AD_%E5%9F%BA%E4%BA%8E%E5%A7%94%E6%89%98%E8%AE%A2%E5%8D%95%E6%95%B0%E6%8D%AE%E7%9A%84alpha%E5%9B%A0%E5%AD%90_17%E9%A1%B5_2mb.pdf)

[20191029-东方证券-因子选股系列研究之六十\_基于量价关系度量股票的买卖压力.pdf](/jiawei.tang/order_apb/uploads/694fcdaf5354ea8485f68557d5ad42b9/20191029-%E4%B8%9C%E6%96%B9%E8%AF%81%E5%88%B8-%E5%9B%A0%E5%AD%90%E9%80%89%E8%82%A1%E7%B3%BB%E5%88%97%E7%A0%94%E7%A9%B6%E4%B9%8B%E5%85%AD%E5%8D%81_%E5%9F%BA%E4%BA%8E%E9%87%8F%E4%BB%B7%E5%85%B3%E7%B3%BB%E5%BA%A6%E9%87%8F%E8%82%A1%E7%A5%A8%E7%9A%84%E4%B9%B0%E5%8D%96%E5%8E%8B%E5%8A%9B.pdf)     

研报回测数据：2010-6-30 ~ 2019     

#### 着重复现、改进研报中以下三个订单因子： 
- 早盘买卖订单量大小比
- 订单价格分歧度
- 订单数据改进的APB因子

数据来源：
```python
    order_pth = f"/data/HighFreqData/Order/l2order/{pd.to_datetime(trading_date).strftime('%Y%m%d')}.parquet"  A：新增委托订单   L: 限价单
    trade_pth = f"/data/cephfs/transaction/{pd.to_datetime(trading_date).strftime('%Y%m%d')}.parquet"
    min_pth = "/data/HighFreqData/MinuteQuote/new_minute/one_minute/{pd.to_datetime(trading_date).strftime('%Y%m%d')}.parquet"
    JYDB     DZ_AdjustingFactor     DZ_PriceLimit      ReturnDaily
```
因子降频到日频后均进行了 20d rolling     

测试时间：2021-05-18 ~ 2024-12-31（Version 2 逐笔委托数据只有2021.5.18开始的）        

回测选项： 全市场、行业中性、只对lncap中性化、行业均值回填缺失值   

主要改进方式：
- 区分买卖方向
- 分时间段处理
- 因子构造方式
- 极端值处理方式
- 与实时收益率回归取残差

主要难点：
- 数据多为高频数据，需考虑计算速度
- 部分订单因子对合成因子所用到的价格及其敏感，订单价格极值处理需格外在意


### Stage Two：问题分析、进一步改进与测试

由于改进因子均只需要用到订单数据，进行了部分回填，测试时间：2019-01-01 ~ 2025-05-31     

主要工作：    

- 基于建议进一步改进研报中的三个因子     
- 订单价格极值处理：探究合理性与必要性     
- 对效果较好的订单因子统一进行缩尾处理(对订单价格缩尾）     
- 研究分钟频因子与分钟收益率关系（暴露度、相关性），寻找可解释性    
- 提取出20个效果较好的因子，根据相关性和实际意义分为四类，最终产出4个因子考虑上生产      

<details>
<summary>20个有效因子总结</summary>

有效因子总结issue中总结了如下20个因子的原始回测表现与20d滚动后回测表现,以及因子构造方式。       

1.缩尾订单价格分歧程度因子（8）   
  
- 每日时间段： 9：30 ~ 10：00；  10：00 ~ 14：30；    14：30 ~ 14：57       
- Bid Side：对订单价格进行\[P01, P99\]的缩尾
- Ask Side：对订单价格进行\[P03, P97\]的缩尾
- 买卖双方分钟频分歧度因子：9：30 ~ 14：57 


2. 基于主笔委托买方数据构建的APB 因子 （3）     

- 原始日频
- 分钟频降维为日频
- 跨日复权版5日均值


3. 分钟频因子与分钟频收益率的暴露度因子 （8）     

a. 分钟频\[P01,P99\]缩尾订单价格分歧度与分钟频收益率的分组切割因子     
- 买方：低分钟收益率组平均分钟价格分歧度；  高分钟收益率组平均分钟价格分歧度     
- 卖方：低分钟收益率组平均分钟分歧度； 高分钟收益率组平均分钟价格分歧度；  低价格分歧度组平均分钟收益率；  高价格分歧度组平均分钟收益率        

b. 分钟频\[P01,P99\]缩尾委托买单APB与分钟频收益率的分组切割因子       
- 高分钟apb组平均分钟收益率作为因子       
- 高分钟收益率组平均分钟APB作为因子       


4. 分钟频委托买单APB与分钟频收益率的相关性因子 （1）

[汇总因子比较性测试.pdf](https://github.com/user-attachments/files/21573701/default.pdf)


</details>



<details>
<summary>最终成果汇总</summary>

#### 买方分歧度因子

- 合成方式：10：00-14：30 与 14：30-14：57 两个时间段的20d滚动买方分歧度因子zscore标准化后等权相加等全相加
 <details>
<summary>原始因子结果</summary>
![image](/uploads/0f3af8ff4283ee47adaea532360329d1/image.png)
![image](/uploads/1946e3a72036cbf27fe0015772562c2d/image.png)
</details>

 <details>
<summary>最终结果</summary>
![image](/uploads/d62355c9cf115475fa094414508d394a/image.png)
![image](/uploads/515a374e9dd692385889f2d00c50cd68/image.png)
</details>

<details>
<summary>增量测试</summary>
![image](/uploads/34bc292e45460ee38830607d82157fd8/image.png)
</details>

#### 卖方分歧度因子

- 合成方式：10：00-14：30 与 14：30-14：57 两个时间段的20d滚动卖方分歧度因子zscore标准化后等权相加等全相加

<details>
<summary>原始因子结果</summary>
![image](/uploads/46c9895489b51178c54d25b04160cf14/image.png)
![image](/uploads/2ea79f9d99041c872800722f88b0fdc9/image.png)
</details>

 <details>
<summary>最终结果</summary>
![image](/uploads/dbb7afc4be2b965ec9da40db8c904425/image.png)
![image](/uploads/debee02c6cc85c9d07beee1bd7ced5f0/image.png)
</details>

<details>
<summary>增量测试</summary>
![image](/uploads/001f1009fff68006f6282caa20df5028/image.png)
</details>

#### APB因子

- 合成方式：日频与5天跨日复权20d滚动APB因子zscore标准化后等权相加等全相加
 <details>
<summary>原始因子结果</summary>
![image](/uploads/e84025f086b158fd30d07075807c2408/image.png)
![image](/uploads/bec37e0fa379ab0b008554347cf24eeb/image.png)
</details>

<details>
<summary>最终结果</summary>
![image](/uploads/94bcc28317a32898f6b9ddc524c37a47/image.png)
![image](/uploads/cf5bb8125d8dd5b09a15fc831691c57c/image.png)
</details>


<details>
<summary>增量测试</summary>
![image](/uploads/2359712bf37b42b2f242894eaab2b34d/image.png)
</details>

#### 卖方分歧度与分钟收益率暴露因子

- 合成方式：低卖方价格分歧度组对应分钟平均收益率减去高卖方价格分歧度组对应分钟平均收益率（直接用20d因子值相减即可，与单日相减后在滚动效果完全相同）

<details>
<summary>原始因子结果</summary>
![image](/uploads/6dfe221ae662f11d6885c1d3f9a1b0c6/image.png)
![image](/uploads/398d4ce648d041e4329cc14e2320dfbe/image.png)
</details>

<details>
<summary>最终结果</summary>
![image](/uploads/f6e42c871047360ffd261c57e6ab638e/image.png)
![image](/uploads/c302b0f09d12c3239e19537eeaf1adae/image.png)
</details>

<details>
<summary>增量测试</summary>
![image](/uploads/f929eba2f970bb15cefbd5c32f47bc17/image.png)
</details>


#### 比较测试
![image](/uploads/fa1b73eb2ef39d7b7291c3325db37c01/image.png)
![image](/uploads/e46d52b203a7894894f759217ab84a18/image.png)

</details>

---------



## 卖方分歧度因子构建      

#### 数据准备与说明
- 数据源：使用逐笔委托数据，路径格式为：```/data/cephfs/order/YYYYMMDD.parquet```           
- 回测时间： 2016-06-20 到 2025-06-30        
- 交易日列表为```trading_dates = pd.date_range(start=start_date, end=end_date, freq='D')``` 跳过无原始委托数据的日期                      
- 使用DuckDB进行内存数据处理，用函数1计算某交易日因子，输出日度dataframe；函数2处理单个交易日，保存函数1输出的dataframe，识别并跳过已生成因子或不存在原始委托文件的日期，输出 “日期  bool  状态（已存在or成功算True，不存在原文件或遇到错误算False）”；函数3创建进程池，进行并行计算，输出最终的因子储存目录       
- 负向因子，需要加负号（我统一是最后直接对滚动平滑后的因子取负）    


#### 因子说明

因为前后尝试过不同的买卖方向、切割时间段以及缩尾力度，我原本按以下逻辑处理这三个维度的信息：首先为不同时间段设置sql_query的筛选条件列表，针对每一个时间段分别获取买卖双方基础临时表，计算价格分位数临时表，进行价格缩微得到缩尾表。

      买卖方向: ask 或 bid 
       
      时间段维度：（前闭后开）
           开盘前1：9:15-9:20（pre_open_915_920）
           开盘前2：9:20-9:25（pre_open_920_925）
           早盘：9:30-10:00（early_930_1000）
           主交易时段：10:00-14:30（main_1000_1430）
           尾盘1：14:30-14:57（late_1430_1457）
           尾盘2：14:57-15:00（close_1457_1500）
           连续交易时段：9:30-14:57（continue_930_1457）

      处理方式：p01_p99  p03_p97 

      示例最终因子列名：  ask_main_1000_1430_p03_p97

      理论上最后得到的大表有 2*7*2 列  

最后只需要用到 ```卖方``` ```3%-97%分位数缩尾处理```  ```主交易时段：10:00-14:30（main_1000_1430） 以及  尾盘2：14:57-15:00（close_1457_1500）``` 这个维度下面的2个因子。          
这里我保留了对时间段维度的完整划分，在实际计算时，为了节约时间，可以直接不定义其他时间段的查询。    


#### 因子计算流程
1. 对定义的每个时间段，筛选卖方订单：``` order_type = 'A'``` ``` order_details = 'L'``` ```order_side = -1```    
2. 保留证券代码、order_price, order_volume指标，建立临时表    
3. 异常值缩尾处理： 对每个证券该时段卖方订单价格进行缩尾处理，得到新的临时表    
        
        计算每个证券订单价格的3%和97%分位数
        将低于3%分位数的价格替换为3%分位数值
        将高于97%分位数的价格替换为97%分位数值

4. 在缩尾后的临时表上，，按证券代码分组计算价格分歧度

        4.1 计算该时段各证券加权平均对数价格
                 
                 计算每个订单的订单价格的自然对数值
                 计算 对数价格×订单量
                 将所有订单的"对数价格×订单量"相加，再除以它在该时段的总订单量，得到其加权平均对数价格

        4.2 计算该时段各证券每个订单价格与其加权对数价格的偏离程度：

                  对每个订单，计算其对数价格与加权平均对数价格的差值
                  将差值平方，计算 平方差×订单量
                  将该证券所有订单的"平方差×订单量"相加，再除以它在该时段的总订单量
                  对结果开根号，得到订单量加权的价格标准差，即价格分歧度

5. 根据前序定义的因子类型，把每日因子保存为 [date, security_code, factor1， factor2， ···]格式的parquet文件

#### 对因子进行20天滚动平滑
1. 用```os.path.join```得到输出路径下的所有日度因子parquet文件的pattern
2. 用duckdb读取为一个大表，根据前序定义的因子类型格式为 [date, security_code, factor1， factor2， ···]
2. 对传入的factor——list中的每一列，将security_code作为列，date作为索引，该列因子值为value创建透视表
3. 对透视表rolling取mean（），rolling参数为 window=20， min_window=5，
4. 将计算结果从宽格式转回长格式（日期、证券代码、因子值）
5. 对因子值取负并保存


#### 因子合成
1. 获取 10：00-14：30 与 14：30-14：57 两个时间段的20d滚动平滑后的卖方分歧度因子
2. 对两因子分别进行zscore标准化
3. 将标准化后的因子等权相加等全相加





-------------

## APB 因子构建

#### 数据准备与说明
- 数据源：使用逐笔委托数据，路径格式为：```/data/cephfs/order/YYYYMMDD.parquet```； 复权因子表:```jydb.DZ_AdjustingFactor```；```smartquant.ReturnDaily```              
- 回测时间： 2016-06-20 到 2025-06-30   
- 订单时间在连续交易时段内(9:30:00-14:57:00)，即时间戳介于93000000和145700000之间     
- 对订单价格统一进行1%-99%分位数缩尾处理，最后一步取LN时注意极值处理
- 交易日列表为```trading_dates = pd.date_range(start=start_date, end=end_date, freq='D')``` 跳过无原始委托数据的日期                      
- 使用DuckDB进行内存数据处理，用函数1计算某交易日因子，输出日度dataframe；函数2处理单个交易日，保存函数1输出的dataframe，识别并跳过已生成因子或不存在原始委托文件的日期，输出 “日期  bool  状态（已存在or成功算True，不存在原文件或遇到错误算False）”；函数3创建进程池，进行并行计算，输出最终的因子储存目录   
- 正向因子，不需要取负    


### 日频买方委托订单APB因子

##### 因子计算流程
1. 筛选买方订单：``` order_type = 'A'``` ``` order_details = 'L'``` ```order_side = 1``` ```order_time >= 93000000``` ```order_time <= 145700000```
2. 保留security_code、order_price, order_volume指标，建立临时表    
3. 异常值缩尾处理： 对临时表中每个证券订单价格进行缩尾处理，得到新的临时表    
        
        计算每个证券订单价格的1%和99%分位数
        将低于1%分位数的价格替换为1%分位数值
        将高于99%分位数的价格替换为99%分位数值

4. 在缩尾后的临时表上，按证券代码分组计算两种价格均值，储存在新的表中

        4.1 计算各证券所有订单加权平均价格(TWAP)
                 
                 简单计算该证券所有订单价格的算术平均值
                 TWAP = AVG(order_price)

        4.2 计算各证券的委托量加权平均价格(VWAP)：

                  按订单量加权计算证券所有订单价格的平均值
                  VWAP = SUM(order_price * order_volume) / SUM(order_volume)

5. 计算APB因子：在新表上，按证券代码分组，计算TWAP与VWAP的比值的自然对数
        
                  APB = ln(TWAP / VWAP)
                  异常值处理：如果TWAP或VWAP为零或负值，则APB为空值(NULL)

5. 把保存为 [date, security_code, daily_APB_p01_p99]格式的parquet文件

##### 对因子进行20天滚动平滑
1. 用```os.path.join```得到输出路径下的所有日度因子parquet文件的pattern
2. 用duckdb读取为一个大表，根据前序定义的因子类型格式为 [date, security_code, daily_APB_p01_p99]
2. 将security_code作为列，date作为索引，该daily_APB_p01_p99为value创建透视表
3. 对透视表rolling取mean（），rolling参数为 window=20， min_window=5，
4. 将计算结果从宽格式转回长格式（日期、证券代码、因子值）




### 5天跨日复权版买方委托订单APB因子

##### 日度数据处理

1. 筛选买方订单：``` order_type = 'A'``` ``` order_details = 'L'``` ```order_side = 1``` ```order_time >= 93000000``` ```order_time <= 145700000```
2. 保留security_code、order_price, order_volume指标，添加交易日date字段，建立临时表   
3. 异常值缩尾处理： 对临时表中每个证券订单价格进行缩尾处理，得到新的临时表    
        
        计算每个证券订单价格的1%和99%分位数
        将低于1%分位数的价格替换为1%分位数值
        将高于99%分位数的价格替换为99%分位数值 
4. 日度统计量计算：  对缩尾处理后的数据，计算每只证券每个交易日的以下统计量

        订单价值总和（daily_value_p01_p99）：每个订单的价格与数量的乘积之和，用于后续计算VWAP
        价格总和（daily_sum_price_p01_p99）：所有订单价格的简单加总，用于后续计算TWAP
        订单数量总和（daily_volume_p01_p99）：所有订单数量的总和
        订单笔数（daily_count_p01_p99）：订单的总笔数

5. 得到每天每只股票的汇总数据，储存为日度parquet文件


##### 价格复权处理

1. 复权数据准备：提前保存每个交易日对应的复权因子数据，确保复权因子（AdjustingFactor）和除权除息日期（ExDiviDate）字段可用。

2. 对价格相关统计量复权：只对价格相关字段进行复权，交易量相关字段保持不变

         创建需要复权的字段副本：
               adj_value_p01_p99：对应daily_value_p01_p99的复权版本
               adj_price_p01_p99：对应daily_sum_price_p01_p99的复权版本
        
        复权处理步骤：
               按照除权除息日期从新到旧排序复权因子数据
               对于每个除权除息日期，找出该日期之后（含该日期）且尚未复权的数据
               将这些数据的价格相关字段乘以对应的复权因子
               标记这些数据为已复权状态
               复权后的数据保留原始数据的所有字段，并增加复权后的价格字段。

5. 处理前一步得到的所有日度汇总parquet数据

##### 5日滚动窗口因子计算

1. 滚动窗口数据准备
滚动窗口的数据准备采用两层函数结构，分别是整体调度函数calculate_rolling_average()和单日处理函数process_single_date()。

        整体调度函数calculate_rolling_average()：

               通过glob.glob()函数获取数据目录下所有日度统计数据的Parquet文件列表
               从文件名中提取日期信息（假设文件名格式为"YYYYMMDD.parquet"）
               将日期和对应的文件路径组成元组对，并按日期升序排序，形成file_dates列表
               如果指定了日期范围（start_date和end_date），则筛选出该范围内的文件
               确定需要处理的日期索引列表，从第window_size-1个文件开始（确保每个处理日有足够的历史数据）
               使用多进程并行处理每个日期的数据计算

        单日处理函数process_single_date()：

               接收当前日期索引i、文件日期列表file_dates和窗口大小window_size等参数
               获取当前日期和对应的文件路径
               检查输出文件是否已存在，若存在则跳过处理
               确定滚动窗口的起始索引：start_idx = max(0, i-window_size+1)，确保不会索引到负数
               获取窗口内所有日期的文件路径列表：recent_files = [path for _, path in file_dates[start_idx:i+1]]
               读取这些文件的数据并合并成一个DataFrame
               按证券代码和日期对合并后的数据进行排序，为后续计算做准备

2. 滚动窗口统计量计算

对于每个处理日期，单日处理函数继续执行以下步骤：

        对于该日期对应5日窗口内所有的数据，按证券代码分组计算两种复权平均价格，存为新表

               复权后的委托量加权平均价格（adj_vwap_p01_p99）：窗口内adj_value_p01_p99之和除以窗口内daily_volume_p01_p99之和
               复权后的简单平均价格（adj_twap_p01_p99）：窗口内adj_price_p01_p99之和除以窗口内daily_count_p01_p99之和


3. APB因子计算：在新表上，按证券代码分组，计算Adj_TWAP与Adj_VWAP的比值的自然对数

      5d_apb_p01_p99 = ln(adj_twap_p01_p99 / adj_vwap_p01_p99)
      异常值处理：将计算结果中的正无穷大和负无穷大值替换为NaN

4. 最终因子只保留[date, security_code, 5d_apb_p01_p99]三列，保存输出日度因子parquet文件


##### 对因子进行20天滚动平滑
1. 用```os.path.join```得到输出路径下的所有日度因子parquet文件的pattern
2. 用duckdb读取为一个大表，根据前序定义的因子类型格式为 [date, security_code, 5d_apb_p01_p99]
2. 将security_code作为列，date作为索引，该daily_APB_p01_p99为value创建透视表
3. 对透视表rolling取mean（），rolling参数为 window=20， min_window=5，
4. 将计算结果从宽格式转回长格式（日期、证券代码、因子值）




### 因子合成
1. 获取 日频 与 5天跨日复权 两个版本的20d滚动平滑后的买方委托订单APB因子
2. 对两因子分别进行zscore标准化
3. 将标准化后的因子等权相加等全相加
