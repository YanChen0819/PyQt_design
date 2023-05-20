# PyQt Design : Sqlite 論文查找系統與 WordCloud 視覺化分析
## 課程 : 統計應用軟體設計
### 本應用程式在 VisualStudio 端 Python 開發 ， 操作介面模仿類似 Google 搜尋較為人性設計，並在後端鏈接 sqlite 資料庫，查找功能以 sql 語法撰寫，並做了自然語言處理(NLP)，雖然只是 Count Based Embeddding 中的 TF-IDF 方法，但結合文字雲可剖析其關鍵詞並可經由點選細項得到論文細節，降低論文查找參考文獻的難度。
![img](https://github.com/YanChen0819/PyQt_design/blob/main/guide/Assignement2_ui_1.PNG)
## 點選搜尋圖案或在搜尋框內按 Enter 即可連接資料庫獲得所有論文資料 
![img](https://github.com/YanChen0819/PyQt_design/blob/main/guide/Assignement2_ui_2.PNG)
## 能依照選取的條件進行關鍵字搜尋，例如作者名含有 Chen 的人
![img](https://github.com/YanChen0819/PyQt_design/blob/main/guide/Assignement2_ui_3.PNG)
## 雙擊點選個別資料欄位會產生 Count Base 的文本分析計算關鍵字出現頻率，並以文字雲視覺化
![img](https://github.com/YanChen0819/PyQt_design/blob/main/guide/Assignement2_ui_4.PNG)
