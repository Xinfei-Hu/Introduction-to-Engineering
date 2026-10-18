from safety.core.agent_core.tool_registry import BaseTool
from safety.core.agent_core.datamodels import TaskMemory, BBox
from ultralytics import YOLO
import os


class YoloDetectTool(BaseTool):
    name = "yolo_detect"
    description = "使用YOLOv8做目标检测，输入图片路径，返回检测框和标注图"

    def __init__(self, model_path='yolov8n.pt'):
        # 第一次运行将自动下载 yolov8n.pt 模型
        self.model = YOLO(model_path)

    def run(self, task_memory: TaskMemory, **kwargs):
        image_path = kwargs.get('image_path')
        save_mark_path = kwargs.get('save_mark_path')

        # 效验图片
        if not image_path or not os.path.exists(image_path):
            raise FileNotFoundError(f'图片路径不存在：{image_path}')

        results = self.model(image_path)
        bbox_list: list[BBox] = []
        raw_text_lines = []

        for res in results:
            boxes = res.boxes
            for box in boxes:
                cls_idx = int(box.cls[0])
                cls_name = self.model.names[cls_idx]
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                bbox = BBox(
                    cls_name=cls_name,
                    confidence=conf,
                    x1 = x1, x2 = x2, y1 = y1, y2 = y2,
                )
                bbox_list.append(bbox)
                raw_text_lines.append(f'{cls_name}: {conf:.2f}, box:[{x1, y1, x2, y2}]')
        # 保存标注图片
        if save_mark_path:
            parent_dir = os.path.dirname(save_mark_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            results[0].save(save_mark_path)

        res_text = '\n'.join(raw_text_lines)
        return {
            "bboxes": bbox_list,
            "marked_image_path": save_mark_path,
            "raw_text": res_text
        }


if __name__ == '__main__':
    """自测试代码"""
    mem = TaskMemory.create_new_task('../images/test.jpg', 'image')
    yolo_tool = YoloDetectTool()
    res = yolo_tool.run(mem, image_path='../images/test.jpg', save_mark_path='output_mark.jpg')
    print(res)
    print(res["raw_text"])