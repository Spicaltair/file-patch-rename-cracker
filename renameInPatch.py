import os
import time
import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter import ttk
import threading

def select_folder():
    folder_path = filedialog.askdirectory(title="选择文件夹")
    return folder_path

def count_files(folder_path):
    total_files = 0
    for root, dirs, files in os.walk(folder_path):
        total_files += len(files)
    return total_files

# def update_progress(progress_bar, label, processed_files, total_files, message):
    # label.config(text=message)
    # progress_bar['value'] = processed_files
    # progress_bar.update_idletasks()
def update_progress(progress_bar, label, processed_files, total_files, message):
    # 计算百分比
    percent_complete = (processed_files / total_files) * 100

    # 更新标签上的文字
    label.config(text=f"{message} {percent_complete:.2f}% 完成")

    # 更新进度条
    progress_bar['value'] = processed_files
    progress_bar.update_idletasks()
    
def change_extension_to_xml(folder_path, progress_bar, progress_label, total_files):
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
                update_progress(progress_bar, progress_label, processed_files, total_files * 2, "修改扩展名...")
                continue

            # Handle files without extensions
            if file_ext == '':
                file_ext = 'NO_EXT'

            file_name = file_name.strip()
            file_ext = file_ext.strip()

            # Handle file name conflict
            counter = 1
            new_file_name = f"{file_name}_{counter}.xml"
            new_file_path = os.path.join(root, new_file_name)

            while os.path.exists(new_file_path):
                counter += 1
                new_file_name = f"{file_name}_{counter}.xml"
                new_file_path = os.path.join(root, new_file_name)

            original_extensions[new_file_path] = file_ext

            try:
                os.rename(file_path, new_file_path)
                print(f"重命名成功: {file_path} -> {new_file_path}")
            except Exception as e:
                failed_modifications.append(file_path)
                print(f"无法重命名文件 {file_path} 为 {new_file_path}: {e}")
            
            # Update progress bar
            processed_files += 1
            update_progress(progress_bar, progress_label, processed_files, total_files * 2, "解密中...")

    return original_extensions, failed_modifications

def restore_original_extension(original_extensions, wait_time, progress_bar, progress_label, total_files):
    failed_restorations = []
    processed_files = total_files  # Start from halfway

    for new_file_path, original_ext in original_extensions.items():
        file_name, _ = os.path.splitext(new_file_path)
        if original_ext == 'NO_EXT':
            original_ext = ''

        restored_file_path = file_name + original_ext.strip()

        time.sleep(wait_time)

        try:
            os.rename(new_file_path, restored_file_path)
            print(f"恢复成功: {new_file_path} -> {restored_file_path}")
        except Exception as e:
            failed_restorations.append(new_file_path)
            print(f"无法恢复文件 {new_file_path} 为 {restored_file_path}: {e}")
        
        # Update progress bar
        processed_files += 1
        update_progress(progress_bar, progress_label, processed_files, total_files * 2, "解密中...")

    return failed_restorations

def process_files(folder_path, wait_time, progress_bar, progress_label, total_files, root):
    # Step 1: Change extensions to .xml
    original_extensions, failed_modifications = change_extension_to_xml(folder_path, progress_bar, progress_label, total_files)

    # Step 2: Wait and restore original extensions
    failed_restorations = restore_original_extension(original_extensions, wait_time, progress_bar, progress_label, total_files)

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
        wait_time = simpledialog.askinteger("输入停留时间", "请输入每个文件的停留时间，文件越多越需要时间（秒）:", minvalue=1, initialvalue=15)
        total_files = count_files(folder_path)

        root = tk.Tk()
        root.title("进度条")
        progress_label = tk.Label(root, text="文件处理进度：")
        progress_label.pack(pady=10)

        progress_bar = ttk.Progressbar(root, length=400, mode='determinate', maximum=total_files * 2)
        progress_bar.pack(pady=20)

        thread = threading.Thread(target=process_files, args=(folder_path, wait_time, progress_bar, progress_label, total_files, root))
        thread.start()

        root.mainloop()

    else:
        print("未选择文件夹。")

if __name__ == "__main__":
    main()
