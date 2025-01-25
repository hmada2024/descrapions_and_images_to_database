# image_to_blob_logic.py
import sqlite3
import os
import tempfile
from tkinter import messagebox 

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
    return filename.split()