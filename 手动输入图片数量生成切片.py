import cv2
import os

# 获取当前目录下的所有图片文件（假设以 .jpg 结尾）
image_files = [f for f in os.listdir('.') if f.endswith('.jpg')]
# 按数字顺序排序，而不是字符串排序
image_files.sort(key=lambda x: int(x.split('.')[0]))

total_images = len(image_files)

if total_images == 0:
    print("当前目录下没有找到 .jpg 格式的图片！")
    exit()

# 等待用户输入需要选择的数量
while True:
    try:
        num_to_select = int(input(f"请输入要选择的图片数量（1 - {total_images}）："))
        if 1 <= num_to_select <= total_images:
            break
        else:
            print("输入超出范围，请重新输入！")
    except ValueError:
        print("请输入有效的整数！")

# 计算平均分布的百分比位置
percentages = []
for i in range(num_to_select):
    pct = (i + 0.5) / num_to_select * 100
    percentages.append(pct)

print(f"选择的百分比位置: {[f'{p:.1f}%' for p in percentages]}")

# 计算对应的索引位置
selected_indices = []
for pct in percentages:
    index = int((pct / 100) * total_images)
    index = min(index, total_images - 1)
    selected_indices.append(index)

print(f"总共找到 {total_images} 张图片")
print(f"选择的图片索引: {selected_indices}")
print(f"选择的图片文件: {[image_files[i] for i in selected_indices]}")

# 加载选中的图片
selected_images = []
for i in selected_indices:
    img = cv2.imread(image_files[i])
    if img is None:
        print(f"无法加载图片 {image_files[i]}")
        exit()
    selected_images.append(img)

# 获取第一张图片的尺寸
H, W = selected_images[0].shape[:2]

# 创建条带
strips = []
num_selected = len(selected_images)

for k, img in enumerate(selected_images):
    start_x = int((k / num_selected) * W)
    end_x = int(((k + 1) / num_selected) * W)
    strip = img[:, start_x:end_x]
    strips.append(strip)

final_image = cv2.hconcat(strips)
cv2.imwrite('final_image.jpg', final_image)
print(f"已将选中的 {num_to_select} 张图片拼接为 final_image.jpg")
