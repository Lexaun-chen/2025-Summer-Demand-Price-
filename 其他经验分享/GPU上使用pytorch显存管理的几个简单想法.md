在我做可转债的定价中，算法的空间复杂度比较大，特别是当我们需要满足收敛性的时候，需要大大增加路径数量，从而可能会导致内存的崩溃。因此，对于内存管理，我这里分享一些简单的tips，或许可以给大家一些思路。

# 在bash中手动查看当前gpu的使用情况：

```bash
nvidia-smi   # 查看当前的状态
nvidia-smi -l 2 # 每两秒刷新一次，l:loop; 2:频率
```

```bash
(venv1) [qiminma@hpc-g04 lsm]$ nvidia-smi
Fri Aug  1 09:42:56 2025       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 575.57.08              Driver Version: 575.57.08      CUDA Version: 12.9     |
|-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  NVIDIA GeForce RTX 4090        Off |   00000000:01:00.0 Off |                  Off |
| 32%   33C    P8             14W /  450W |       1MiB /  24564MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   1  NVIDIA GeForce RTX 4090        Off |   00000000:25:00.0 Off |                  Off |
| 31%   33C    P8             13W /  450W |       1MiB /  24564MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   2  NVIDIA GeForce RTX 4090        Off |   00000000:41:00.0 Off |                  Off |
| 32%   34C    P8             21W /  450W |       1MiB /  24564MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   3  NVIDIA GeForce RTX 4090        Off |   00000000:81:00.0 Off |                  Off |
| 31%   33C    P8             12W /  450W |       1MiB /  24564MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   4  NVIDIA GeForce RTX 4090        Off |   00000000:C1:00.0 Off |                  Off |
| 31%   33C    P8             16W /  450W |       1MiB /  24564MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   5  NVIDIA GeForce RTX 4090        Off |   00000000:E1:00.0 Off |                  Off |
| 31%   40C    P2            152W /  450W |   14130MiB /  24564MiB |     57%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
                                                                                         
+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|    5   N/A  N/A         3012835      C   ./lsm_gpu                             14120MiB |
+-----------------------------------------------------------------------------------------+
```

- P8: 性能状态
- P0-P2：高性能状态
- P8：低功耗/空闲状态
- 152W / 450W: 当前功耗 / 最大功耗上限
- 14130MiB / 24564MiB: 已用显存 / 总显存
- 57%: GPU利用率

# 内存优化思路1：及时释放变量
- del tensor 是删除变量，准备释放内存。
- torch.cuda.empty_cache() 是清理 PyTorch 的显存缓存，让显存真正归还给系统。

```python
import torch

# 未优化版本：变量累积
def unoptimized():
    tensors = []
    for _ in range(100):
        tensors.append(torch.randn(1000, 1000).cuda())
    return torch.cuda.max_memory_allocated()

# 优化版本：及时释放
def optimized():
    max_mem = 0
    for _ in range(100):
        tensor = torch.randn(1000, 1000).cuda()
        max_mem = max(max_mem, torch.cuda.memory_allocated())
        del tensor 
        torch.cuda.empty_cache()
    return max_mem

print(f"未优化内存: {unoptimized()/1024**2:.2f} MB")
print(f"优化后内存: {optimized()/1024**2:.2f} MB")
```

```bash
未优化内存: 400.00 MB 优化后内存: 3.81 MB
```

# 内存优化思路2：梯度累加

```python
model = torch.nn.Transformer(d_model=256).cuda()
optimizer = torch.optim.Adam(model.parameters())

# 直接大批次训练 (batch_size=64)
def large_batch():
    torch.cuda.reset_peak_memory_stats()
    inputs = torch.randn(64, 100, 256).cuda()
    targets = torch.randn(64, 100, 256).cuda()
    
    outputs = model(inputs, targets)
    loss = torch.nn.MSELoss()(outputs, targets)
    loss.backward()
    optimizer.step()
    return torch.cuda.max_memory_allocated()

# 梯度累加 (等效batch_size=64)
def gradient_accumulation():
    torch.cuda.reset_peak_memory_stats()
    accum_steps = 4
    optimizer.zero_grad()
    
    for i in range(accum_steps):
        inputs = torch.randn(16, 100, 256).cuda()  # 实际batch_size=16
        targets = torch.randn(16, 100, 256).cuda()
        
        outputs = model(inputs, targets)
        loss = torch.nn.MSELoss()(outputs, targets) / accum_steps
        loss.backward()
    
    optimizer.step()
    return torch.cuda.max_memory_allocated()

print(f"大批次内存: {large_batch()/1024**2:.2f} MB")
print(f"梯度累加内存: {gradient_accumulation()/1024**2:.2f} MB")
```

```bash
大批次内存: 2520.47 MB 梯度累加内存: 903.73 MB
```

# 内存优化思路3：混合精度训练(AMP)

- with autocast('cuda'): 作用域内的大部分张量计算（如矩阵乘法、卷积等）会自动用 float16（或 bfloat16，取决于硬件和设置），以节省显存和加速运算。
- 但有些操作（比如损失计算、归一化、部分累加等）会自动保持 float32，以保证数值稳定性。

```python
from torch.amp import autocast, GradScaler

model = torch.nn.Transformer(d_model=512, batch_first=True).cuda()
scaler = GradScaler('cuda')

# 全精度训练，全部使用Float32
def full_precision():
    torch.cuda.reset_peak_memory_stats()
    inputs = torch.randn(32, 100, 512).cuda()
    targets = torch.randn(32, 100, 512).cuda()
    outputs = model(inputs, targets)
    loss = torch.nn.MSELoss()(outputs, targets)
    loss.backward()
    return torch.cuda.max_memory_allocated()

# 混合精度训练，部分使用Float32

def mixed_precision():
    torch.cuda.reset_peak_memory_stats()
    inputs = torch.randn(32, 100, 512).cuda()
    targets = torch.randn(32, 100, 512).cuda()
    with autocast('cuda'):
        outputs = model(inputs, targets)
        loss = torch.nn.MSELoss()(outputs, targets)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
    return torch.cuda.max_memory_allocated()

print(f"全精度内存: {full_precision()/1024**2:.2f} MB")
print(f"混合精度内存: {mixed_precision()/1024**2:.2f} MB")
```

# 内存优化思路4：cpu-gpu异步传输

gpu的显存只有24G，很多时候我们可以在cpu中储存数据，然后将需要用来计算的数据传到gpu上。但是如果追求高性能的话，单纯的cpu-gpu可能会有很多性能开销

### 4.1 pin memory

##### 为何通常会勾选Pin Memory？
 
- 避免内存交换：计算机运行时，系统可能将不常用的内存数据暂时转移到硬盘的虚拟内存中（swap空间），以释放物理内存。但对于需要快速访问的场景（如高性能计算、实时数据处理、GPU与CPU的数据交互），这种交换会导致严重的延迟。勾选Pin Memory可阻止数据被换出，保证数据始终在物理内存中，确保快速访问。
- 提升数据传输效率：在GPU计算中，CPU需要将数据传输到GPU显存。如果数据所在的内存被锁定，GPU可以直接通过DMA（直接内存访问）技术快速读取，无需CPU额外参与，减少数据传输的耗时和开销。

![image](/uploads/15519440edb8d0bbe672a67940a46b23/image.png)

##### 何时避免使用

- 数据密集程度低的任务或小型数据集
- 内存有限的系统（不过这种系统的话，大规模训练也没啥意义）

### 4.2 non_blocking

##### Why non_blocking

- 当数据从主机内存（CPU）传输到设备内存（GPU）时，默认情况下，这种传输是阻塞的。也就是说，当前操作会等待数据传输完成后，才会继续执行其他操作。
- 设置 non_blocking=True 后，如果条件满足，数据传输会变成异步操作。这样主机可以在传输数据的同时执行其他任务，从而提高程序的整体效率。

##### 使用方式

**注意，必须是pin_memory=True!!**

```python
# 创建一个张量
tensor = torch.randn(1000, 1000)

# 阻塞方式移动到GPU
gpu_tensor = tensor.to('cuda', non_blocking=False)  # default

# 非阻塞方式移动到GPU
gpu_tensor = tensor.to('cuda', non_blocking=True)

```
```python
# 在训练循环中
for data, target in dataloader:
    # 非阻塞方式将数据移动到GPU
    data = data.to(device, non_blocking=True)
    target = target.to(device, non_blocking=True)
    
    # CPU现在可以开始准备下一批数据，而不必等待当前数据传输完成
    output = model(data)  # 这里会自动等待数据传输完成后执行
    loss = criterion(output, target)
    ...
```

##### 生效条件

- 数据必须存储在主机的“固定内存”（Pinned Memory）中

```
1. DMA传输的先决条件
DMA(直接内存访问)是允许GPU直接从内存读取数据而无需CPU干预的机制，但它有严格的要求：

物理内存地址必须固定：DMA引擎需要知道确切的物理内存位置，而不只是虚拟地址
内存区域必须连续：DMA传输需要连续的内存块
内存不能被分页或交换：在传输过程中，内存内容不能变化

2. 非固定内存的传输过程
当数据在普通(可分页)内存中时，即使设置non_blocking=True，以下步骤是不可避免的：
地址转换：系统需要将虚拟地址转换为物理地址
内存检查：验证数据是否在物理内存中，如果在交换空间需要先换入
内存复制：CPU必须创建一个临时固定内存缓冲区
数据复制：将数据从可分页内存复制到这个临时固定缓冲区
GPU传输：最后才能发起到GPU的传输
这整个过程需要CPU主动参与每一步，无法并行执行，因此即使指定了非阻塞操作，也会变成实质上的同步传输。
```

- 目标设备必须GPU

##### 深度学习中的意义

- 深度学习模型训练中：训练时，数据加载与 GPU 计算可以重叠进行。例如，在 GPU 处理当前 batch 的同时，下一 batch 的数据可以异步传输到 GPU。
