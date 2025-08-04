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
