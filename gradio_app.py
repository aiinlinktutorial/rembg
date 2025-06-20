import gradio as gr
from rembg import remove
from PIL import Image
import io

def remove_background(image):
    """
    去除图片背景的函数
    """
    if image is None:
        return None
    
    # 将图片转换为字节流
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # 使用rembg去除背景
    output = remove(img_byte_arr)
    
    # 将结果转换回PIL图像
    result_image = Image.open(io.BytesIO(output))
    
    return result_image

# 创建Gradio界面
iface = gr.Interface(
    fn=remove_background,
    inputs=gr.Image(type="pil", label="上传图片"),
    outputs=gr.Image(type="pil", label="去除背景后的图片"),
    title="🎨 Rembg - AI智能背景去除工具",
    description="上传任意图片，AI会自动为您去除背景！支持人像、动物、物品等各种图片类型。",
    examples=[
        ["examples/girl-1.jpg"],
        ["examples/animal-1.jpg"],
        ["examples/car-1.jpg"]
    ] if True else None,  # 如果examples文件夹存在
    allow_flagging="never"
)

if __name__ == "__main__":
    print("🚀 正在启动Gradio界面...")
    print("📝 启动后请在浏览器中打开显示的链接")
    print("🎯 上传图片即可自动去除背景！")
    iface.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    ) 