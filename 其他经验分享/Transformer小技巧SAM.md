## 背景

我尝试用Transformer来预测沪深300指数的realized_vol，一开始性能好像不尽如人意。 <br>
下面的小优化是我根据一篇论文进行的尝试，确实对我的预测有一些帮助，但是可能并不针对所有应用场景都有效，仅供参考。大家有什么好的想法一定一定跟我说一声！感谢！ <br>

## 原因

将Transformer应用到时间序列预测中泛化能力较差可能有两个主要的原因 <br>
1. 注意力熵崩溃现象<br>
研究者发现Transformer存在一个严重问题：<br>
在训练的最初阶段（第一个epoch后），注意力矩阵就迅速"固定"<br>
之后的训练过程中，注意力矩阵几乎不再变化<br>
这意味着模型很早就决定了"关注什么"，而不是通过学习逐渐优化注意力<br>
<br>

2. 锐度问题<br>
锐度是损失函数曲面的陡峭程度<br>
高锐度意味着参数的微小变化会导致损失大幅波动<br>
Transformer的损失曲面比其他架构更"崎岖"<br>
这导致训练不稳定和泛化性能差<br>

## 解决方案: 锐度感知最小化(SAM)

#### SAM的核心思想是寻找"平坦最小值"而非"尖锐最小值"：

1. 基本原理：<br>
不仅最小化当前参数的损失<br>
还最小化参数周围小扰动后的最大损失<br>

2. 损失函数的数学表达：<br>
L_train(ω) = max{L_train(ω + ε)}<br>
ω是模型参数，ε是小扰动<br>

3. 直观理解：<br>
传统训练：找到损失函数的低点<br>
SAM训练：找到损失函数的"平坦谷底"（周围点也都是低损失）<br>

## SAMformer

除了SAM之外，研究者还提出了一个Transformer用于预测时间序列数据的轻量级实现。如果我们要进行日频的预测，那么样本量相对于Transformer的参数量而言较小，因而轻量级实现是有意义的。研究者提出的是一个单层、单头注意力的轻量级实现。令人惊讶的是，这个简单的模型在多个标准数据集上显著超越了现有的复杂模型。<br>

但是根据我的复现，RevIN层不添加可能效果更好，但是这可能是基于我的数据，所以也建议大家都尝试一下。<br>
此外，我感觉这个模型效果还不错也是因为加了残差连接。<br>

<img width="202" height="345" alt="image" src="https://github.com/user-attachments/assets/d0fd197e-5007-40a3-b64d-9b32393d5fa8" />
<br>

```python
class RevIN(nn.Module):

    def __init__(self, num_features, eps=1e-5, affine=True):
        super(RevIN, self).__init__()
        self.num_features = num_features
        self.eps = eps
        self.affine = affine
        
        if affine:
            self.gamma = nn.Parameter(torch.ones(num_features))
            self.beta = nn.Parameter(torch.zeros(num_features))
            
    def forward(self, x, mode='norm'):
        # x shape: [batch_size, seq_len, num_features]
        if mode == 'norm':
            self.mean = x.mean(dim=1, keepdim=True)
            self.stdev = torch.sqrt(torch.var(x, dim=1, keepdim=True, unbiased=False) + self.eps)
            x_normalized = (x - self.mean) / self.stdev
            
            if self.affine:
                x_normalized = x_normalized * self.gamma.view(1, 1, -1) + self.beta.view(1, 1, -1)
                
            return x_normalized
            
        elif mode == 'denorm':
            if self.affine:
                x = (x - self.beta.view(1, 1, -1)) / self.gamma.view(1, 1, -1)
                
            x_denormalized = x * self.stdev + self.mean
            return x_denormalized
        
        else:
            raise ValueError(f"Mode {mode} not recognized. Use 'norm' or 'denorm'")

class SAMformer(nn.Module):
    def __init__(self, input_dim=9, d_model=16, output_dim=1, nhead=1, dropout=0):
        super(SAMformer, self).__init__()
        self.input_dim = input_dim
        self.d_model = d_model
        self.output_dim = output_dim

        self.revin = RevIN(input_dim)
        self.input_embedding = nn.Linear(input_dim, d_model)
        
        # 自注意力组件
        self.query = nn.Linear(d_model, d_model)
        self.key = nn.Linear(d_model, d_model)
        self.value = nn.Linear(d_model, d_model)
        self.attention = nn.MultiheadAttention(d_model, nhead, batch_first=True, dropout=dropout)
        self.attn_output = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(d_model, input_dim)
        self.final_projection = nn.Linear(input_dim, output_dim)
    
    def forward(self, x):

        batch_size, seq_len, _ = x.shape        
        x_normalized = self.revin(x, mode='norm')
        embedded = self.input_embedding(x_normalized)

        # 自注意力计算
        q = self.query(embedded)
        k = self.key(embedded)
        v = self.value(embedded)
        
        attn_output, _ = self.attention(q, k, v)
        attn_output = self.attn_output(attn_output)
        
        # 跳跃连接
        output = embedded + self.dropout(attn_output)
        
        # 使用最后一个时间步的输出进行预测
        last_step = output[:, -1, :]
        full_dim_prediction = self.fc(last_step)  # [batch_size, input_dim]
        full_dim_prediction = full_dim_prediction.unsqueeze(1)  # [batch_size, 1, input_dim]
        denormalized = self.revin(full_dim_prediction, mode='denorm')  # [batch_size, 1, input_dim]
        denormalized = denormalized.squeeze(1)  # [batch_size, input_dim]
        final_output = self.final_projection(denormalized)  # [batch_size, output_dim]
        final_output = self.fc(last_step)  # [batch_size, output_dim]
        
        return final_output
```
> 参考文献： https://github.com/romilbert/samformer

> SAM.py： https://github.com/davda54/sam/blob/main/sam.py
