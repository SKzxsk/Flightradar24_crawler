import cv2
import os

# 获取当前目录下的所有图片文件
image_files = [f for f in os.listdir('.') if f.endswith('.jpg')]
image_files.sort()  # 按文件名排序

# 照片数量
num_images = len(image_files)

if num_images == 0:
    print("当前目录下没有找到 .jpg 格式的图片！")
    exit()

images = [cv2.imread(img) for img in image_files]
if any(img is None for img in images):
    print("无法加载图片，请检查文件格式或路径！")
    exit()

H, W = images[0].shape[:2]
strips = []

for k, img in enumerate(images):
    start_x = int((k / num_images) * W)
    end_x = int(((k + 1) / num_images) * W)
    strip = img[:, start_x:end_x]
    strips.append(strip)

final_image = cv2.hconcat(strips)
cv2.imwrite('final_image.jpg', final_image)
print(f"已将 {num_images} 张图片拼接为 final_image.jpg")
