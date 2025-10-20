# 功能規格：顯示目錄中的 EXIF 狀態

## 1. 目標

讓使用者在選擇目錄後，能快速概覽目錄下所有圖片的 EXIF 狀態（特別是相機製造商、相機型號和鏡頭型號）。這將幫助使用者識別哪些圖片需要更新，而無需逐一檢查。

## 2. 使用者故事

身為一個使用者，
當我選擇一個包含照片的目錄時，
我想要看到該目錄中所有圖片檔案的列表，
這樣我就可以看到每張圖片的「相機製造商」、「相機型號」和「鏡頭型號」EXIF 標籤是已經存在還是缺失。

## 3. 建議變更

### 3.1. GUI 介面變更

-   **新元件：** 在「選擇目錄」按鈕下方新增一個新的框架（Frame）或樹狀檢視（Treeview）元件。
-   **功能：**
    -   當選擇目錄後，這個新區域將會填入該目錄中所有支援的圖片檔案列表。
    -   列表應顯示檔案名稱和關鍵 EXIF 標籤的狀態。
    -   **欄位：**
        1.  `檔案名稱`：圖片的檔案名稱。
        2.  `相機製造商`：EXIF `Make` 標籤的值，如果沒有則顯示「缺失」。
        3.  `相機型號`：EXIF `Model` 標籤的值，如果沒有則顯示「缺失」。
        4.  `鏡頭型號`：EXIF `LensModel` 標籤的值，如果沒有則顯示「缺失」。
-   **互動：** (未來增強功能) 點擊列表中的檔案可以將其現有的 EXIF 資料載入到上方的輸入欄位中。現階段僅為顯示功能。

### 3.2. 後端邏輯變更 (`exif_editor.py`)

-   **新函式：** 建立一個新函式，例如 `get_exif_summary_from_directory(directory_path, target_extensions)`。
-   **函式邏輯：**
    -   此函式將掃描指定目錄中的圖片檔案。
    -   對於每張圖片，它將使用 `piexif.load()` 來讀取 EXIF 資料。
    -   它將特別檢查 `piexif.ImageIFD.Make`、`piexif.ImageIFD.Model` 和 `piexif.ExifIFD.LensModel` 是否存在及其值。
    -   它將返回一個包含字典或物件的列表，其中每個項目代表一個檔案，並包含其名稱和目標 EXIF 標籤的值。
    -   **返回結構範例：**
        ```python
        [
            {'filename': 'photo1.jpg', 'make': 'SONY', 'model': 'ILCE-7M3', 'lens_model': 'FE 24-105mm F4 G OSS'},
            {'filename': 'photo2.jpg', 'make': 'Canon', 'model': 'Canon EOS R5', 'lens_model': '缺失'},
            {'filename': 'photo3.arw', 'make': '缺失', 'model': '缺失', 'lens_model': '缺失'}
        ]
        ```

### 3.3. 整合 (`gui.py`)

-   `ExifEditorGUI` 中的 `select_directory` 方法將被更新。
-   選擇目錄後，它將呼叫新的後端函式 (`get_exif_summary_from_directory`)。
-   然後，結果將用於填充 GUI 中的新樹狀檢視元件。
-   此過程應在單獨的執行緒中運行，以防止在讀取所有檔案的 EXIF 資料時 GUI 凍結。

## 4. 驗收標準

-   [x] 在專案根目錄中建立一個名為 `feature.md` 的新檔案。
-   [x] 後端邏輯：在 `exif_editor.py` 中實作 `get_exif_summary_from_directory` 函式。
-   [x] 文字模式功能：建立 `query_exif_cli.py`，可接收目錄參數並在終端機中印出 EXIF 摘要。
-   [x] 圖形化介面 (GUI) 整合：在主視窗中顯示 EXIF 摘要。
    -   [x] 當使用者選擇目錄時，會顯示圖片列表。
    -   [x] 列表顯示每張圖片的檔案名稱、相機製造商、相機型號和鏡頭型號。
    -   [x] 如果圖片的 EXIF 資料中不存在某個標籤，則該標籤的欄位顯示「缺失」。
    -   [x] 在應用程式讀取 EXIF 資料時，GUI 保持回應。
