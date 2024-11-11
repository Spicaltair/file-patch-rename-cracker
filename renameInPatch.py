import os
import time
import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter import ttk
import threading

# 版本 1.4 - 增加进度条和后台线程
# 日期：2024年10月17日

def change_extension_to_xml(folder_path, progress_bar, total_files):
    original_extensions = {}
    failed_modifications = []
    processed_files = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_name, file_ext = os.path.splitext(file)

            # Skip files that are already .xml
            if file_ext.lower() == '.xml':
                processed_files += 1
                progress_bar.step(1)
                progress_bar.update_idletasks()
                continue

            # Handle files without extensions
            if file_ext == '':
                file_ext = 'NO_EXT'

            # Strip spaces from file name and extension
            file_name = file_name.strip()
            file_ext = file_ext.strip()

            new_file_name = f"{file_name}_{counter}.xml"
            new_file_path = os.path.join(root, new_file_name)

            # Handle file name conflict
            counter = 1
            while os.path.exists(new_file_path):
                new_file_name = f"{file_name}_{counter}.xml"
                new_file_path = os.path.join(root, new_file_name)
                counter += 1

            original_extensions[new_file_path] = file_ext

            try:
                os.rename(file_path, new_file_path)
                print(f"重命名成功: {file_path} -> {new_file_path}")
            except Exception as e:
                failed_modifications.append(file_path)
                print(f"无法重命名文件 {file_path} 为 {new_file_path}: {e}")
            
            # Update progress bar
            processed_files += 1
            progress_bar.step(1)
            progress_bar.update_idletasks()

    return original_extensions, failed_modifications

def restore_original_extension(original_extensions, wait_time, progress_bar, total_files):
    failed_restorations = []
    processed_files = 0

    for new_file_path, original_ext in original_extensions.items():
        file_name, _ = os.path.splitext(new_file_path)
        if original_ext == 'NO_EXT':
            original_ext = ''

        restored_file_path = file_name + original_ext.strip()

        # Wait for the specified time before restoring each file
        time.sleep(wait_time)

        try:
            os.rename(new_file_path, restored_file_path)
            print(f"恢复成功: {new_file_path} -> {restored_file_path}")
        except Exception as e:
            failed_restorations.append(new_file_path)
            print(f"无法恢复文件 {new_file_path} 为 {restored_file_path}: {e}")
        
        # Update progress bar
        processed_files += 1
        progress_bar.step(1)
        progress_bar.update_idletasks()

    return failed_restorations

def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="请选择要操作的文件夹")
    return folder_path

def count_files(folder_path):
    file_count = 0
    for root, dirs, files in os.walk(folder_path):
        file_count += len(files)
    return file_count

def process_files(folder_path, wait_time, progress_bar, total_files, root):
    # Step 1: Change extensions to .xml
    original_extensions, failed_modifications = change_extension_to_xml(folder_path, progress_bar, total_files)

    # Step 2: Wait and restore original extensions
    failed_restorations = restore_original_extension(original_extensions, wait_time, progress_bar, total_files)

    # Output summary
    print(f"\n所有文件的扩展名已修改，并成功恢复到原始状态。")
    if failed_modifications:
        print(f"\n修改为xml时失败的文件: {len(failed_modifications)}")
        for f in failed_modifications:
            print(f)
    
    if failed_restorations:
        print(f"\n恢复原扩展名时失败的文件: {len(failed_restorations)}")
        for f in failed_restorations:
            print(f)

    # Close progress bar window after completion
    root.quit()

def main():
    folder_path = select_folder()

    if folder_path:
        # Prompt user for wait time
        wait_time = simpledialog.askinteger("输入停留时间", "请输入每个文件的停留时间（秒）:", minvalue=1, initialvalue=15)

        # Count total number of files
        total_files = count_files(folder_path)

        # Initialize the progress bar window
        root = tk.Tk()
        root.title("进度条")
        progress_label = tk.Label(root, text="文件处理进度：")
        progress_label.pack(pady=10)

        progress_bar = ttk.Progressbar(root, length=400, mode='determinate', maximum=total_files * 2)
        progress_bar.pack(pady=20)

        # Run file processing in a background thread
        thread = threading.Thread(target=process_files, args=(folder_path, wait_time, progress_bar, total_files, root))
        thread.start()

        root.mainloop()

    else:
        print("未选择文件夹。")

if __name__ == "__main__":
    main()
