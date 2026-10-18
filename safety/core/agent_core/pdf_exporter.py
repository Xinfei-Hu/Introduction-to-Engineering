import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from PIL import Image as PILImage

# 导入项目内模型
from safety.core.agent_core.datamodels import TaskMemory

# 全局注册中文字体，只执行一次
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
FONT_NAME = "STSong-Light"


class PdfExporter:
    """
    OOP 工地安全检测PDF导出器
    对接本项目多Agent流水线TaskMemory，生成A4检测报告，包含整改建议列
    """
    # 配置常量，统一在这里修改
    PAGE_SIZE = A4
    MAX_IMG_WIDTH_MM = 160
    MAX_IMG_HEIGHT_MM = 180

    def __init__(self):
        self.styles = getSampleStyleSheet()
        # 构建样式（实例化时一次性创建）
        self.title_style = ParagraphStyle(
            'ReportTitle',
            parent=self.styles["Heading1"],
            fontName=FONT_NAME,
            fontSize=18,
            alignment=1,
            spaceAfter=10*mm
        )
        self.normal_style = ParagraphStyle(
            'ReportNormal',
            parent=self.styles["Normal"],
            fontName=FONT_NAME,
            fontSize=11
        )

    @staticmethod
    def get_scaled_image(img_path: str, max_width_mm: float, max_height_mm: float):
        """静态方法：读取图片，按宽高限制等比例缩放，返回reportlab图片对象"""
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"图片文件不存在：{img_path}")
        max_width = max_width_mm * mm
        max_height = max_height_mm * mm
        with PILImage.open(img_path) as im:
            w, h = im.size
            ratio = w / h
            new_w_by_width = max_width
            new_h_by_width = new_w_by_width / ratio

            # 如果按宽度缩放后的高度超过最大高度，则改用高度限制
            if new_h_by_width > max_height:
                new_h = max_height
                new_w = new_h * ratio
            else:
                new_w = new_w_by_width
                new_h = new_h_by_width
        return Image(img_path, width=new_w, height=new_h)

    def build_hazard_table(self, hazard_list):
        """构造隐患表格：隐患类型｜风险等级｜隐患描述｜整改建议"""
        table_data = [
            [
                Paragraph("隐患类型", self.normal_style),
                Paragraph("风险等级", self.normal_style),
                Paragraph("隐患描述", self.normal_style),
                Paragraph("整改建议", self.normal_style)
            ]
        ]
        # 4列宽度分配
        col_widths = [30 * mm, 20 * mm, 55 * mm, 55 * mm]

        if hazard_list and len(hazard_list) > 0:
            for hazard in hazard_list:
                row = [
                    Paragraph(hazard.danger_type, self.normal_style),
                    Paragraph(hazard.risk_level, self.normal_style),
                    Paragraph(hazard.description, self.normal_style),
                    Paragraph(hazard.suggestion, self.normal_style)
                ]
                table_data.append(row)
        else:
            row = [
                Paragraph("无隐患", self.normal_style),
                Paragraph("-", self.normal_style),
                Paragraph("现场未发现安全违规", self.normal_style),
                Paragraph("保持现有作业规范", self.normal_style)
            ]
            table_data.append(row)

        table = Table(table_data, colWidths=col_widths)
        table_style = TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('BACKGROUND', (0, 0), (-1, 0), '#dddddd'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])
        table.setStyle(table_style)
        return table

    def build_conflict_table(self, conflict_logs):
        """构建Agent冲突记录表（课题亮点）"""
        if not conflict_logs or len(conflict_logs) == 0:
            return None
        table_data = [
            [Paragraph("冲突编号", self.normal_style), Paragraph("冲突描述", self.normal_style)]
        ]
        for idx, item in enumerate(conflict_logs):
            # 适配你的冲突字典key
            conflict_text = item["conflict"]
            row = [
                Paragraph(f"{idx+1}", self.normal_style),
                Paragraph(conflict_text, self.normal_style)
            ]
            table_data.append(row)
        table = Table(table_data, colWidths=[30*mm, 130*mm])
        table_style = TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('BACKGROUND', (0, 0), (-1, 0), '#E8F0FE'),
            ('GRID', (0, 0), (-1, -1), 1, '#000000'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])
        table.setStyle(table_style)
        return table

    def export(self, pdf_save_path: str, original_img_path: str, marked_img_path: str, task_mem: TaskMemory, hazard_list):
        """
        主导出方法
        :param pdf_save_path: PDF输出路径
        :param original_img_path: 原始图片路径
        :param marked_img_path: YOLO标注框图片路径
        :param task_mem: TaskMemory任务上下文（包含conflict_logs）
        :param hazard_list: 复核完成后的隐患列表 review输出结果
        """
        # 自动创建保存目录
        out_dir = os.path.dirname(pdf_save_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        doc = SimpleDocTemplate(pdf_save_path, pagesize=self.PAGE_SIZE)
        story = []

        # 报告头部信息
        report_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story.append(Paragraph("施工现场安全隐患检测报告", self.title_style))
        story.append(Spacer(1, 5 * mm))
        story.append(Paragraph(f"报告生成时间：{report_time}", self.normal_style))
        story.append(Paragraph(f"任务ID：{task_mem.task_id}", self.normal_style))
        story.append(Spacer(1, 5 * mm))

        risk_count = len(hazard_list)
        story.append(Paragraph(f"隐患总数量：{risk_count} 处", self.normal_style))
        story.append(Spacer(1, 5 * mm))

        # 原图
        story.append(Paragraph("【原始图片】", self.normal_style))
        img_origin = self.get_scaled_image(original_img_path, self.MAX_IMG_WIDTH_MM, self.MAX_IMG_HEIGHT_MM)
        story.append(img_origin)
        story.append(Spacer(1, 5 * mm))

        # YOLO标注图
        story.append(Paragraph("【YOLO目标标注图】", self.normal_style))
        img_mark = self.get_scaled_image(marked_img_path, self.MAX_IMG_WIDTH_MM, self.MAX_IMG_HEIGHT_MM)
        story.append(img_mark)
        story.append(Spacer(1, 8 * mm))

        # 隐患表格（带整改建议）
        risk_table = self.build_hazard_table(hazard_list)
        story.append(Paragraph("【识别隐患清单】", self.normal_style))
        story.append(risk_table)
        story.append(Spacer(1, 6 * mm))

        # 多Agent冲突记录（课题亮点）
        conflict_logs = getattr(task_mem, "conflict_logs", [])
        if conflict_logs and len(conflict_logs) > 0:
            story.append(Paragraph("【多智能体意见冲突记录】", self.normal_style))
            conflict_table = self.build_conflict_table(conflict_logs)
            story.append(conflict_table)

        doc.build(story)
        print(f"PDF报告生成成功：{pdf_save_path}")
        return pdf_save_path


if __name__ == "__main__":
    # 本地自测入口，正式项目运行不会执行这里
    pass