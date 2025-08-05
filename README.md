# EXIF Editor

這是一個使用 Python 和 `tkinter` 開發的圖形化介面工具，可以讓您輕鬆編輯圖片檔案的 EXIF 中繼資料。

## 功能

*   **編輯作者資訊**: 新增或修改圖片的作者資訊。
*   **編輯版權資訊**: 新增或修改圖片的版權聲明。
*   **編輯相機與鏡頭型號**: 
    *   使用下拉式選單快速選取曾經輸入過的相機與鏡頭型號。
    *   歷史紀錄會自動儲存於 `config/config.ini`。
*   **自動更新 UserComment**: `UserComment` 欄位會根據您選擇的相機與鏡頭型號自動填入。
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
    *   點擊 "Select Directory" 選擇整個資料夾。
    *   在對應的欄位輸入或選擇您想要的 EXIF 資訊。
    *   點擊 "Save & Start Processing" 按鈕，程式將會更新所選圖片的 EXIF 資訊。

## 相依套件

本專案使用到的套件將會列在 `requirements.txt` 檔案中。

*   `piexif`

## 設定

您可以在 `config/config.ini` 檔案中設定預設的 EXIF 資訊，以及相機和鏡頭的歷史紀錄：

```ini
[EXIF]
artist = Your Name
copyright = Your Copyright
model = Your Camera
lensmodel = Your Lens

[History]
camera_models = Your Camera,Another Camera
lens_models = Your Lens,Another Lens
```

## 授權

本專案採用 MIT 授權。
