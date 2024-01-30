# 帕魯配種世界線

## 執行畫面

- 選擇擁有的帕魯
![](/doc_img/p1.png)
- 查看可配種出的帕魯
  - **左邊欄位**選擇想配種出的帕魯
  - **右邊欄位**查看可行的配方，點選配方可以在左邊欄位的相應帕魯顯示框框
  - **含同代/不含同代按鈕**切換配方顯示條件：
    - 配方只包含前代帕魯 (若選第N代的帕魯，只會採用已擁有的帕魯 + 第1 ~ N-1代的帕魯組合)
![](/doc_img/p2_2.png)
    - 配方包含同代帕魯 (若選第N代的帕魯，只會採用已擁有的帕魯 + 第1 ~ N代的帕魯組合)
![](/doc_img/p3.png)

## Run

執行 app.exe

## Python (開發者用)
### Create Env

Python版本3.6.13，更高的也能跑
```
pip install pandas
pip install pygame
```

### Run Python

```
python app.py
```

### Package to EXE

安裝封裝套件
```
pip install auto-py-to-exe
```
執行封裝
```
auto-py-to-exe
```