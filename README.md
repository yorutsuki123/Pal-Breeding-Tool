# 帕魯配種世界線

## 執行畫面

- 選擇擁有的帕魯
  - **切換模式按鈕**可切換是否考慮性別：
    - **模式：考慮性別**<br><img src="/doc_img/pp4.png" width="500">
    - **模式：不論性別**<br><img src="/doc_img/pp1.png" width="500">
- 查看可配種出的帕魯
  - **左邊欄位**選擇想配種出的帕魯
  - **右邊欄位**查看可行的配方，點選配方可以在左邊欄位的相應帕魯顯示框框
  - **切換模式按鈕**可切換是否考慮同代的帕魯 (下圖為選擇擁有的帕魯時，選擇**模式：考慮性別**之畫面)：
    - **模式：不含同代** (若選第N代的帕魯，只會採用已擁有的帕魯 + 第1 ~ N-1代的帕魯組合)<br><img src="/doc_img/pp5.png" width="500">
    - **模式：包含同代** (若選第N代的帕魯，只會採用已擁有的帕魯 + 第1 ~ N代的帕魯組合)<br><img src="/doc_img/pp6.png" width="500">
  - 選擇擁有的帕魯時，選擇**模式：不論性別**之畫面
    - **模式：不含同代**<br><img src="/doc_img/pp2.png" width="500">
    - **模式：包含同代**<br><img src="/doc_img/pp3.png" width="500">

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
