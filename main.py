import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os
import tempfile
import time  # استيراد مكتبة الوقت

class ImageToBlobApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("نظام إدارة الصور والبيانات النصية")
        self.geometry("800x600")

        # إنشاء علامة تبويب لإدارة تحويل الصور
        self.image_to_blob_tab = ImageToBlobTab(self)
        self.image_to_blob_tab.pack(fill="both", expand=True)

class ImageToBlobTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db_path = tk.StringVar()
        self.image_table = tk.StringVar()
        self.image_column = tk.StringVar()
        self.audio_column = tk.StringVar()
        self.segments_table = tk.StringVar()
        self.segment_column = tk.StringVar()
        self.full_text_column = tk.StringVar()
        self.segment_order_column = tk.StringVar() # عمود ترتيب القطع
        self.image_folder_path = tk.StringVar()

        self.setup_widgets()

    def setup_widgets(self):
        # إطار قاعدة البيانات
        db_frame = ttk.LabelFrame(self, text="إعدادات قاعدة البيانات")
        db_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(db_frame, text="مسار قاعدة البيانات:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(db_frame, textvariable=self.db_path, width=50).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(db_frame, text="تصفح", command=self.browse_database).grid(row=0, column=2, padx=5, pady=2)

        # إطار جدول الصور
        image_table_frame = ttk.LabelFrame(self, text="جدول الصور")
        image_table_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(image_table_frame, text="اسم الجدول:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.image_table_combo = ttk.Combobox(image_table_frame, textvariable=self.image_table, state="readonly")
        self.image_table_combo.grid(row=0, column=1, padx=5, pady=2)
        self.image_table_combo.bind("<<ComboboxSelected>>", self.on_image_table_selected)

        ttk.Label(image_table_frame, text="عمود الصور:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.image_column_combo = ttk.Combobox(image_table_frame, textvariable=self.image_column, state="readonly")
        self.image_column_combo.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(image_table_frame, text="عمود الصوت:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.audio_column_combo = ttk.Combobox(image_table_frame, textvariable=self.audio_column, state="readonly")
        self.audio_column_combo.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(image_table_frame, text="عمود النص الكامل:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.full_text_column_combo = ttk.Combobox(image_table_frame, textvariable=self.full_text_column, state="readonly")
        self.full_text_column_combo.grid(row=3, column=1, padx=5, pady=2)


        # إطار جدول الأجزاء
        segments_table_frame = ttk.LabelFrame(self, text="جدول الأجزاء")
        segments_table_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(segments_table_frame, text="اسم الجدول:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.segments_table_combo = ttk.Combobox(segments_table_frame, textvariable=self.segments_table, state="readonly")
        self.segments_table_combo.grid(row=0, column=1, padx=5, pady=2)
        self.segments_table_combo.bind("<<ComboboxSelected>>", self.on_segments_table_selected)

        ttk.Label(segments_table_frame, text="عمود التقطيع:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.segment_column_combo = ttk.Combobox(segments_table_frame, textvariable=self.segment_column, state="readonly")
        self.segment_column_combo.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(segments_table_frame, text="عمود ترتيب القطع:").grid(row=2, column=0, padx=5, pady=2, sticky="w") # Label for the new column
        self.segment_order_column_combo = ttk.Combobox(segments_table_frame, textvariable=self.segment_order_column, state="readonly")
        self.segment_order_column_combo.grid(row=2, column=1, padx=5, pady=2) # Combo for the new column

        # إطار الصور
        image_frame = ttk.LabelFrame(self, text="مجلد الصور")
        image_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(image_frame, text="مسار المجلد:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Entry(image_frame, textvariable=self.image_folder_path, width=50).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(image_frame, text="تصفح", command=self.browse_images_folder).grid(row=0, column=2, padx=5, pady=2)

        # عناصر التحكم
        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.pack(pady=10)

        ttk.Button(self, text="بدء المعالجة", command=self.process_images).pack(pady=5)

    def browse_database(self):
        path = filedialog.askopenfilename(filetypes=[("SQLite Databases", "*.db")])
        if path:
            self.db_path.set(path)
            self.update_tables()

    def update_tables(self):
        conn = sqlite3.connect(self.db_path.get())
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        self.image_table_combo['values'] = tables
        self.segments_table_combo['values'] = tables
        conn.close()

    def on_image_table_selected(self, event=None):
        table = self.image_table.get()
        self.update_columns(table, self.image_column_combo)
        self.update_columns(table, self.audio_column_combo)
        self.update_columns(table, self.full_text_column_combo)

    def on_segments_table_selected(self, event=None):
        table = self.segments_table.get()
        self.update_columns(table, self.segment_column_combo)
        self.update_columns(table, self.segment_order_column_combo) # Update the segment order column combo
        

    def update_columns(self, table, combo):
        conn = sqlite3.connect(self.db_path.get())
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info('{table}')")
        columns = [row[1] for row in cursor.fetchall()]
        combo['values'] = columns
        conn.close()

    def browse_images_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.image_folder_path.set(path)

    def process_images(self):
        db_path = self.db_path.get()
        image_folder = self.image_folder_path.get()
        image_table = self.image_table.get()
        image_column = self.image_column.get()
        audio_column = self.audio_column.get()
        segments_table = self.segments_table.get()
        segment_column = self.segment_column.get()
        full_text_column = self.full_text_column.get() # الحصول على عمود النص الكامل
        segment_order_column = self.segment_order_column.get() # Get segment order column

        required_fields = [
            db_path,
            image_folder,
            image_table,
            image_column,
            segments_table,
            segment_column,
            segment_order_column
        ]

        if not all(required_fields):
            messagebox.showerror("خطأ", "الرجاء تحديد جميع الحقول المطلوبة.")
            return

        process_images_folder(
            db_path=db_path,
            image_folder=image_folder,
            image_table=image_table,
            image_column=image_column,
            audio_column=audio_column,
            segments_table=segments_table,
            segment_column=segment_column,
            full_text_column=full_text_column,
            segment_order_column=segment_order_column,
            progress=self.progress
        )

def process_images_folder(db_path, image_folder, image_table, image_column, audio_column, segments_table, segment_column, full_text_column, segment_order_column, progress):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        total_files = len([f for f in os.listdir(image_folder)
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
        progress['maximum'] = total_files
        processed = 0

        for filename in os.listdir(image_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                img_path = os.path.join(image_folder, filename)

                # تحميل الصورة
                with open(img_path, 'rb') as f:
                    img_blob = f.read()

                # إدخال البيانات في جدول الصور (مع الصوت إذا كان موجودًا)
                if audio_column:
                    cursor.execute(
                        f"INSERT INTO {image_table} ({image_column}, {audio_column}) VALUES (?, ?)",
                        (img_blob, None) # يمكنك هنا توفير قيمة الصوت إذا كان ذلك مطلوبًا
                    )
                else:
                      cursor.execute(
                        f"INSERT INTO {image_table} ({image_column}) VALUES (?)",
                        (img_blob,)
                    )

                # ادخال النص الكامل في الجدول الأساسي
                if full_text_column:
                    description = os.path.splitext(filename)[0]
                    cursor.execute(
                        f"UPDATE {image_table} SET {full_text_column} = ? WHERE ROWID = last_insert_rowid()",
                        (description,)
                    )

                image_id = cursor.lastrowid
                

                # معالجة الأجزاء النصية
                description = os.path.splitext(filename)[0]
                segments = split_filename(description)
                for i, segment in enumerate(segments): #تعديل هنا لاضافة الترتيب
                    cursor.execute(
                        f"INSERT INTO {segments_table} ({segment_column}, image_id, {segment_order_column}) VALUES (?, ?, ?)",
                        (segment, image_id, i + 1) # قم بتعيين الترتيب هنا
                    )


                processed += 1
                progress['value'] = processed
                conn.commit()

        messagebox.showinfo("نجاح", "تم معالجة جميع الصور بنجاح!")

    except Exception as e:
        messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
    finally:
        if conn:
            conn.close()

def split_filename(filename):
    words = filename.split()
    segments = []
    current_segment = []

    for word in words:
        if len(word) > 3:
            if current_segment:
                 segments.append(' '.join(current_segment))
                 current_segment = []
            segments.append(word)
        else:
            current_segment.append(word)
            if sum(len(w) for w in current_segment) >= 3 or len(words) == len(current_segment):
                segments.append(' '.join(current_segment))
                current_segment = []

    if current_segment:
        segments.append(' '.join(current_segment))

    return segments


if __name__ == "__main__":
    app = ImageToBlobApp()
    app.mainloop()