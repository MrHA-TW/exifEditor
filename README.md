# EXIF Editor

這是一個使用 Python 和 `tkinter` 開發的圖形化介面工具，可以讓您輕鬆編輯圖片檔案的 EXIF 中繼資料。

## 功能

*   **編輯作者資訊**: 新增或修改圖片的作者資訊。
*   **編輯版權資訊**: 新增或修改圖片的版權聲明。
*   **編輯相機型號**: 修改拍攝照片的相機型號。
*   **備份與清理**: 在修改前自動備份原始檔案，並提供腳本來清理這些備份。
*   **設定檔**: 透過 `config.ini` 輕鬆設定預設值。

## 如何使用

1.  **安裝相依套件**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **執行主程式**:
    ```bash
    python src/gui.py
    ```

3.  **使用介面**:
    *   點擊 "Select Image" 選擇您想編輯的單張圖片，或點擊 "Select Directory" 選擇整個資料夾。
    *   在 "Artist" 和 "Copyright" 欄位輸入您想要的文字。
    *   點擊 "Update EXIF" 按鈕，程式將會更新所選圖片的 EXIF 資訊。

## 相依套件

本專案使用到的套件將會列在 `requirements.txt` 檔案中。

*   `piexif`

## 設定

您可以在 `config/config.ini` 檔案中設定預設的作者和版權資訊：

```ini
[DEFAULT]
artist = Your Name
copyright = Your Copyright
```

## 授權

本專案採用 MIT 授權。
