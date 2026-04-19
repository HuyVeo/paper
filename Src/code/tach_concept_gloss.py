import os
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
input_file = os.path.join(base_dir, 'test.txt')
output_file1 = os.path.join(base_dir, 'file1.txt')
output_file2 = os.path.join(base_dir, 'file2.txt')

def process_data():
    if not os.path.exists(input_file):
        print(f"Lỗi: Không tìm thấy file '{input_file}' trong thư mục này.")
        return
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file1, 'w', encoding='utf-8') as f1, \
             open(output_file2, 'w', encoding='utf-8') as f2:
            
            for line in infile:
                line = line.strip() 
                if not line:
                    continue 

                if ',' in line:
                    part1, part2 = line.split(',', 1)
                    f1.write(part1.strip() + '\n')
                    f2.write(part2.strip() + '\n')
                else:
                    f1.write(line + '\n')
                    f2.write('\n')

    except Exception as e:
        print(f"Có lỗi xảy ra rồi: {e}")
    print("đã chạy thành công")

if __name__ == "__main__":
    process_data()