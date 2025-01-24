import os
import PyInstaller.__main__

def create_exe(script_path, app_name, icon_path=None, additional_files=None,use_windowed=True):
    """
    يقوم بإنشاء ملف تنفيذي من تطبيق بايثون باستخدام PyInstaller.

    Args:
        script_path (str): مسار ملف بايثون الرئيسي لتطبيقك.
        app_name (str): الاسم الذي سيظهر للملف التنفيذي.
        icon_path (str, optional): مسار الأيقونة التي سيتم استخدامها للملف التنفيذي. Defaults to None.
        additional_files (list, optional): قائمة بمسارات الملفات أو المجلدات الإضافية التي يجب تضمينها في الملف التنفيذي. Defaults to None.
        use_windowed(bool, optional): لمنع ظهور الشاشه السوداء (true). Defaults to True.
    """

    command = [
        script_path,
        '--name', app_name,
        '--onefile',
    ]
    
    if use_windowed:
      command.append('--windowed')
    else:
      command.append('--noconsole')


    if icon_path:
        command.extend(['--icon', icon_path])

    if additional_files:
      for file in additional_files:
        command.extend(['--add-data', f'{file};.'])

    PyInstaller.__main__.run(command)

if __name__ == "__main__":
    # معلومات التطبيق
    script_path = 'main.py'  # استبدل بمسار ملف بايثون الرئيسي لتطبيقك
    app_name = 'MyEnglishApp'  # استبدل باسم التطبيق الذي تريده
    icon_path = 'icon.ico'  # استبدل بمسار الأيقونة الخاصة بك (اختياري)
    additional_files = ['assets']# مسار المجلدات والملفات الاضافيه (اختياري)


    # إنشاء الملف التنفيذي
    create_exe(script_path, app_name, icon_path, additional_files)
    print('تم إنشاء الملف التنفيذي بنجاح في مجلد dist!')