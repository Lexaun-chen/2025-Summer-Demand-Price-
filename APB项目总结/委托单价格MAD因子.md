## 委托单价格MAD因子

```math
\text{MAD} = \text{median}(|X_i - \text{median}(X)|)
```
其中，X_i为某股票某日的第i笔委托的订单价格。

我们分买方订单、卖方订单、所有订单，分别构建了日度六个时间段的MAD。

```math
\text{MAD}_{bid} = \text{median}(|X_{bid,i} - \text{median}(X_{bid})|)
```

```math
\text{MAD}_{ask} = \text{median}(|X_{ask,i} - \text{median}(X_{ask})|)
```

```math
\text{MAD}_{combined} = \text{median}(|X_{i} - \text{median}(X)|)
```

- 测试时间： 2019-01-01  ~   2025-05-31


### 简单中位数

- pre_open_915_920

<details>
<summary>回测结果</summary>
<img width="1123" height="801" alt="image" src="https://github.com/user-attachments/assets/5e51cd3d-dcb0-4964-8e41-d7c09778d3fb" />
<img width="1125" height="798" alt="image" src="https://github.com/user-attachments/assets/24ae30ef-665e-458c-bed8-4b14f4154d62" />
<img width="1131" height="798" alt="image" src="https://github.com/user-attachments/assets/20f32b5b-8044-4bfa-bd6a-82c3628d9268" />

</details>

- pre_open_920_925
 
<details>
<summary>回测结果</summary>
<img width="1124" height="793" alt="image" src="https://github.com/user-attachments/assets/7e20ee49-c4c7-4596-b4e7-84af26c2d967" />
<img width="1126" height="796" alt="image" src="https://github.com/user-attachments/assets/ba0627af-7d8b-48ea-8ca8-00960924e389" />
<img width="1129" height="790" alt="image" src="https://github.com/user-attachments/assets/3ab54d0e-414c-492c-829b-0b537cfd269e" />

</details>

- early_930_1000
<details>
<summary>回测结果</summary>
![image](/uploads/cd028b15fa97b4f1384df877df4ec054/image.png)
![image](/uploads/388b983170d39726af0a8c48551b12fc/image.png)
![image](/uploads/51059387e4d4f46bf27c6926f819564d/image.png)
</details>

- main_1000_1430

<details>
<summary>回测结果</summary>
<img width="1126" height="792" alt="image" src="https://github.com/user-attachments/assets/cc092601-c2b8-4e98-9bb8-58297b4032fc" />
<img width="1124" height="791" alt="image" src="https://github.com/user-attachments/assets/8aaabe96-acbd-4a00-be4e-717bac993807" />
<img width="1125" height="796" alt="image" src="https://github.com/user-attachments/assets/d0b61e7e-d88f-411b-903b-1b7ca39b11b9" />
</details>

- late_1430_1457
<details>
<summary>回测结果</summary>

<img width="1127" height="790" alt="image" src="https://github.com/user-attachments/assets/69f9694e-3203-47b5-a9f6-7c023a75cbb9" />
<img width="1126" height="797" alt="image" src="https://github.com/user-attachments/assets/675aa1f1-519b-4c75-9639-2b772529092c" />
<img width="1130" height="794" alt="image" src="https://github.com/user-attachments/assets/f5a59d0c-eb1c-49e8-8582-055c35b26769" />

</details>

- close_1457_1500

<details>
<summary>回测结果</summary>
<img width="1123" height="796" alt="image" src="https://github.com/user-attachments/assets/2ac0aabd-57a0-4775-9c82-de5d686dad4d" />
<img width="1120" height="797" alt="image" src="https://github.com/user-attachments/assets/53e5d642-94da-48ce-9254-3bee98e568a7" />

<img width="1126" height="796" alt="image" src="https://github.com/user-attachments/assets/c9eff14d-110e-460f-b2e9-9b2f120a4bd6" />

</details>



### Volume累计中位数构造


- close_1457_1500
<details>
<summary>回测结果</summary>
<img width="1127" height="793" alt="image" src="https://github.com/user-attachments/assets/ee6036c6-3538-4665-9099-064eef1eba0f" />
<img width="1126" height="798" alt="image" src="https://github.com/user-attachments/assets/b73e2e32-4797-446d-9958-4a9091188bd7" />
<img width="1125" height="791" alt="image" src="https://github.com/user-attachments/assets/5595ebad-a919-4d63-8c59-ab6213cb860f" />

</details>

