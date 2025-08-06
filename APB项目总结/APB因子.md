## APB 因子
#### 定义：
```math
 区间内vwap:区间内成交量加权成交价格
```
```math
月度 APB_{i,m} = \ln \left( \frac{\frac{1}{T}\sum_{t=1}^{T}vwap_{i,m}^t}{\frac{\sum_{t=1}^{T}volu_{i,m}^t \cdot vwap_{i,m}^t}{\sum_{t=1}^{T}volu_{i,m}^t}} \right)          
```
```math
日度 APB_{i,d} =  \ln \left( \frac{\frac{1}{T}\sum_{t=1}^{T}vwap_{i,t}^t}{vwap_{i,d}} \right) = \ln \left( \frac{twap_{i,d}}{vwap_{i,d}} \right)
```
<details>
<summary>研报重点信息摘录</summary>    

1. 因子构建逻辑：

         成交量在价格低位更大时买压更大，成交量在价格高位相对更大时卖压较大

         日度APB因子的分子twap相当于区间内vwap的简单平均,分母为区间内vwap与区间内成交量的加权平均
         
         twap/vwap反映成交价的分布情况-> 价格高位的成交量与价格低位成交量的大小对比 -> 刻画买卖压力
         
         APB 取值越大，股票面临的买压越大，卖压越小，收益应该越好

2. 研报结果：买压大的股票平均表现更好，分组收益基本满足单调性
</details>   

### 前期工作

- 基于one-min 成交数据构建的研报中的原始日度APB因子      

<details>
<summary>初始结果</summary>
<img width="1122" height="791" alt="image" src="https://github.com/user-attachments/assets/f31ffc57-5be9-4113-a5f4-e74196993c72" />


</details>

- 基于委托与成交数据改进日度APB因子
<details>
<summary>a.针对分母的改进</summary>  
改进操作：将APB 因子分母中的**区间内成交量加权平均价格**（分母的vwap)替换为**买单委托量加权平均价格**，价格定义为新增该委托时的最新成交价格    

```math
\text{买单加权平均价格} = \frac{\sum \text{买单委托量} \cdot \text{新增该委托时的最新成交价格}}{\sum \text{买单委托量}}
```  
<details>
<summary>改进逻辑</summary>    
1. 核心目标：更好的刻画买压

         twap/vwap反映成交价的分布情况-> 价格高位的成交量与价格低位成交量的大小对比 -> 刻画买卖压力

         分母：成交量加权平均价格 -> 买单委托量加权平均价格；分子：未改变，仍用one-min成交数据计算
         
         twap/vwap反映买方预期的买入价分布-> 价格高位的买单委托量与价格低位委托量的大小对比 -> 刻画买方压力
</details>

- 委托表与成交表的时间对齐问题：以秒为单位做切割，对齐订单委托时间和交易成交时间。 

对于 *新增该委托时的最新成交价格* 我们做了如下两种尝试    

1. 用新增该委托对应那一秒内的成交价格的成交量加权平均值作为最新成交价格，若缺失则直接用订单价格补全。    

<img width="1121" height="793" alt="image" src="https://github.com/user-attachments/assets/31092e8a-1036-45a0-9b06-d46558e123df" />


2. 直接使用买单的订单价格
<img width="928" height="654" alt="image" src="https://github.com/user-attachments/assets/d84ae51e-737a-4638-9cef-2ea40be2d964" />

</details>

<details>
<summary>b.分子分母同步的改进：完全基于买方委托数据构造APB因子</summary>  

- 改进逻辑：由于上面直接使用订单价格的因子效果更好，尝试将分子也替换为买单的订单价格的均值，并将分子分母频率统一，希望能更好的刻画买方预期的买入价分布

##### 1.DTD 分子分母统一用订单买单数据日度均值计算
<img width="1122" height="789" alt="image" src="https://github.com/user-attachments/assets/bb83719d-fa4e-49d1-9d2f-f8a71ad6e10a" />

##### 2. MTM 分子分母统一为订单分钟频因子1d_Rolling版
<img width="1119" height="791" alt="image" src="https://github.com/user-attachments/assets/f8c301c3-1db6-4f56-b27c-a701081638d2" />

</details>

### 后续尝试
#### 1.完善买方委托数据构造的APB因子

             a.在日度和分钟频的基础上补充了跨日复权(5d)的版本
             b.尝试不同的平滑滚动时间：20d、30d
             c.对委托价格进行不同程度的缩尾
<details>
<summary>2019-01-01 ~ 2025-05-31 买方APB全历史回测<\summary>

##### 1. 分钟频
- 20d Rolling
<img width="1129" height="798" alt="image" src="https://github.com/user-attachments/assets/612200c8-56cf-4ef7-8699-bed0929905c7" />


<details>
<summary>  Winsorize </summary>
<img width="1127" height="792" alt="image" src="https://github.com/user-attachments/assets/f7373b1d-c347-4586-afcd-4d753cd93e1d" />
<img width="1125" height="797" alt="image" src="https://github.com/user-attachments/assets/82fc6d0d-00ff-40da-b117-59dce417774a" />

</details>

- 30d Rolling
<img width="1128" height="801" alt="image" src="https://github.com/user-attachments/assets/376c7d37-a3b3-446d-83c4-0ed46b72a9e5" />


<details>
<summary>  Winsorize </summary>
![image](/uploads/f0817fded2ab75e10a551435f4b0d6f9/image.png)
![image](/uploads/19c06a112c07c58afc450bac20f8b6b8/image.png)
</details>

##### 2. 日频
- 20d Rolling
<img width="1126" height="800" alt="image" src="https://github.com/user-attachments/assets/808b4705-5365-4700-816a-b346beef1908" />
  

<details>
<summary>  Winsorize </summary>
<img width="1128" height="798" alt="image" src="https://github.com/user-attachments/assets/cdf3ea69-8449-4c2f-80ea-ee31a35883cc" />
<img width="1129" height="796" alt="image" src="https://github.com/user-attachments/assets/b5d971cf-fa41-4471-8973-bd778beeb8d9" />


</details>


- 30d Rolling
<img width="1126" height="796" alt="image" src="https://github.com/user-attachments/assets/1c87419a-8f90-4692-97e6-7450bb16f6ad" />


<details>
<summary>  Winsorize </summary>
<img width="1128" height="792" alt="image" src="https://github.com/user-attachments/assets/cdca4946-a099-4cb9-aca6-f126bdef29b2" />
<img width="1128" height="797" alt="image" src="https://github.com/user-attachments/assets/c392a457-cff0-4e98-b07b-724d478a7dd8" />

</details>      


##### 3. 5天跨日均值日频

- 20d Rolling
<img width="1126" height="790" alt="image" src="https://github.com/user-attachments/assets/bae2b2ed-017f-4140-9979-d5962a09f715" />


<details>
<summary>  Winsorize </summary>
<img width="1125" height="799" alt="image" src="https://github.com/user-attachments/assets/408c6a7d-b507-4969-a1da-1c6556213ade" />

<img width="1125" height="793" alt="image" src="https://github.com/user-attachments/assets/ea2ace23-6d3e-4e49-9bbe-c2b9bff4e46e" />

</details>        

- 30d Rolling
<img width="1123" height="792" alt="image" src="https://github.com/user-attachments/assets/9e9c5eb3-f570-462b-b9ab-d48f1ad3d625" />
 

<details>
<summary> Winsorize </summary>
<img width="1129" height="798" alt="image" src="https://github.com/user-attachments/assets/e0f60cb4-6d8b-4878-95ef-3bd64229477b" />
<img width="1124" height="791" alt="image" src="https://github.com/user-attachments/assets/289968e3-e004-4023-8f90-299c40d756ab" />

</details>     


##### 统一选择百分之一缩尾，测相关性    
<img width="709" height="921" alt="image" src="https://github.com/user-attachments/assets/121ca0ac-3c12-4519-9ec7-1c9ef421ad8b" />


##### 可解释性：分钟频委托买单APB与分钟频收益率的分组关系         
<img width="1488" height="1189" alt="image" src="https://github.com/user-attachments/assets/fac9fd04-9ae2-4069-a078-978706162063" />

  



#### 2.基于卖方委托数据构造APB因子      
<details>
<summary> 2019-01-01 ~ 2025-05-31 委托单卖方APB全历史回测</summary>  

##### 1. 分钟频     

- 20d Rolling
<img width="1126" height="792" alt="image" src="https://github.com/user-attachments/assets/83fe6019-1a03-4dac-96b2-335a1bab496c" />


- 30d Rolling
<img width="1123" height="794" alt="image" src="https://github.com/user-attachments/assets/9c0728f3-5d73-4a98-9313-671d4f0d9aa4" />


##### 2. 日频
- 20d Rolling
<img width="1126" height="796" alt="image" src="https://github.com/user-attachments/assets/3f3e8690-b5b6-4151-b402-8c6b590f9c61" />

- 30d Rolling
<img width="1125" height="792" alt="image" src="https://github.com/user-attachments/assets/c1633627-3bd4-423d-a1b1-b5c563f380c8" />


##### 3. 5天均值日频     
- 20d Rolling
<img width="1124" height="799" alt="image" src="https://github.com/user-attachments/assets/5d348e93-623a-41c3-9402-882fa8487f5a" />

- 30d Rolling
<img width="1126" height="798" alt="image" src="https://github.com/user-attachments/assets/3731ec56-996e-485a-a0ee-ec0d6795a30d" />

</details>     

  


#### 3.基于成交数据数据构造APB因子      
<details>
<summary> 2019-01-01 ~ 2025-05-31 成交单全历史回测 </summary>     

##### 1. 分钟频      
- 20d Rolling
<img width="1122" height="795" alt="image" src="https://github.com/user-attachments/assets/15787f14-24cb-4292-9f68-399a7b7d8e29" />

- 30d Rolling
<img width="1128" height="798" alt="image" src="https://github.com/user-attachments/assets/f30bfee8-1dfc-4949-9bfd-23b2d95850b7" />

 
##### 2. 日频     
- 20d Rolling     
<img width="1124" height="798" alt="image" src="https://github.com/user-attachments/assets/d5ec7968-f778-4575-8f78-bc5cbdaaa4ee" />

- 30d Rolling
<img width="1123" height="802" alt="image" src="https://github.com/user-attachments/assets/23c9cde7-a9cd-4edf-8f9a-15e56eea5300" />


##### 3. 5天均值日频      

- 20d Rolling
<img width="1126" height="798" alt="image" src="https://github.com/user-attachments/assets/06698c7a-6e38-497d-876b-6c3fed64d927" />


- 30d Rolling
<img width="1126" height="795" alt="image" src="https://github.com/user-attachments/assets/29ee11ba-84cc-48dd-a362-5e53262d8288" />


</details>







### 分钟频委托买单APB与分钟频收益率的暴露度分析

##### 用分钟收益率分组：
- 低分钟收益率平均apb
<img width="1128" height="792" alt="image" src="https://github.com/user-attachments/assets/3cab358f-9eca-44d2-a171-858c53bb1892" />

- 高分钟收益率平均apb
<img width="1127" height="796" alt="image" src="https://github.com/user-attachments/assets/b96d666a-6992-443b-b4a7-088ed2fc1044" />


##### 用APB分组：
- 低apb组平均分钟收益率
<img width="1126" height="787" alt="image" src="https://github.com/user-attachments/assets/8153cd93-c8e0-492c-b61a-e129454e0219" />

- 高apb组平均分钟收益率
<img width="1126" height="797" alt="image" src="https://github.com/user-attachments/assets/186fb8cb-cfe3-4415-95b2-05b47e640c5f" />



### 分钟频委托买单APB与分钟频收益率的相关性    

- 整体相关性: -0.011749453063636015
<img width="381" height="371" alt="image" src="https://github.com/user-attachments/assets/96ffbd33-5161-41e1-be02-5d7048e53a60" />

<img width="1120" height="797" alt="image" src="https://github.com/user-attachments/assets/bbb5854f-fb01-4196-9030-2d4494f519fc" />
<img width="1125" height="796" alt="image" src="https://github.com/user-attachments/assets/2d467540-a2d1-472b-ad92-d5d632089c1e" />
