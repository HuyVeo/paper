import pandas as pd

# 1. Đọc file dữ liệu của bạn
# Thay 'data.csv' bằng tên file thực tế của bạn
df = pd.read_csv(r'D:\MGEEMS\data_cleaned.csv', encoding='utf-8-sig')
# 2. Lấy xen kẽ concept1 và concept2 của từng dòng
# .values.flatten() sẽ biến bảng 2 cột thành 1 danh sách dọc duy nhất
danh_sach_doc = df[['concept1', 'concept2']].values.flatten()

# 3. Ghi vào file txt, mỗi concept nằm trên 1 dòng
with open('ket_qua_danh_sach.txt', 'w', encoding='utf-8-sig') as f:
    for concept in danh_sach_doc:
        f.write(f"{concept}\n")

print("Done! Check file 'ket_qua_danh_sach.txt'")