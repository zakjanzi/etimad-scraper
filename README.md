---

# **Tender Scraper (Crawl4AI)**  
Extracts tender opportunities from [Etimad Saudi Tenders](https://tenders.etimad.sa/) and saves them to an Excel file.  

---

## **🛠 Setup**  
### **1. Get the code**  
You can do that from GitHub by cloning the repo or downloading as zip file.
After that, open the code in any code editor (like VSCode) or use a terminal instead.

### **2. Create a Virtual Environment** 
Navigate to the source folder in your terminal and execute the commands below
#### **Windows**  
```bash
python -m venv venv
venv\Scripts\activate
```
#### **Mac/Linux**  
```bash
python3 -m venv venv
source venv/bin/activate
```

### **3. Install Dependencies**  
```bash
pip install requirements.txt
```

### **4. Set Up Playwright (Browser Automation)**  
```bash
playwright install
```

### **5. Configure API Key**  
Create a `.env` file in the project root and add your [DeepSeek API key](https://platform.deepseek.com/):  
```env
DEEPSEEK_API=your_api_key_here
```

---

## **🚀 Run the Scraper**  
```bash
python main.py
```
- **Output**:  
  - Extracted data → Saved as `tenders.xlsx` in the project folder.  
  - Logs → Printed to the console.  

---

## **⚠️ Troubleshooting**  
### **1. Playwright Browser Errors**  
If you see:  
```plaintext
Executable doesn't exist at /path/to/chromium...
```  
Run:  
```bash
playwright install chromium
```

### **2. Missing Dependencies**  
Ensure `pandas` and `openpyxl` are installed:  
```bash
pip install pandas openpyxl
```

---

## **📁 Output File**  
- **Format**: Excel (`.xlsx`).  
- **Columns**:  
- `اسم المنافسة` (Title)
- `الغرض من المنافسة` (Description) 
- `الرقم المرجعي` (Reference Number)
- `مدة العقد` (Contract Duration)
- `الجهة الحكومية` (Governmental Entity)
- `آخر موعد لإستلام الإستفسارات` (Questions Deadline)
- `آخر موعد لتقديم العروض` (Bid Deadline)
- `مكان التنفيذ` (Location)
- `تاريخ النشر` (Date of Publication)
- `نشاط المنافسة` (Categories/Tags)
- `قيمة وثائق المنافسة` (Bid Price)

---

## **🔧 Customization**  
Edit `main.py` to:  
1. Change the URL (`URL_TO_SCRAPE`).  
2. Modify extracted fields (update `TenderOpportunity` class).  
3. Switch output format (e.g., CSV/JSON → Replace `pd.to_excel()`).  

--- 