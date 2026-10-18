from django.db import models

# Create your models here.

# 检测任务记录表
class DetectionTask(models.Model):
    task_id = models.CharField(max_length=64, unique=True, verbose_name="任务ID")
    task_type = models.CharField(max_length=20, choices=[('image', '图片'), ('video', '视频')], verbose_name="任务类型")
    media_file = models.FileField(upload_to='upload_media/', verbose_name="原始媒体文件")
    pdf_report_path = models.CharField(max_length=256, blank=True, null=True, verbose_name="PDF报告文件夹路径")

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", '等待执行'),
            ("running", '检测中'),
            ("finished", '已完成'),
            ("error", '执行失败'),
        ],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    finish_at = models.DateTimeField(blank=True, null=True)
    pipeline_logs = models.JSONField(blank=True, default=list)
    hazard_list = models.JSONField(blank=True, default=list)

    def __str__(self):
        return f'{self.task_id} [{self.task_type}] {self.status}'

    class Meta:
        verbose_name = "检测任务"
        verbose_name_plural = "检测任务"


# 安全规则 对应 safety_rules.json
class SafetyRule(models.Model):
    rule_key = models.CharField(max_length=128, unique=True, verbose_name='关键词')
    rule_text = models.TextField(verbose_name='安全规范条文')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.rule_key

    class Meta:
        verbose_name = "安全规则"
        verbose_name_plural = "安全规则"


# 复核校验规则 对应 review_verify_rules.json
class ReviewVerifyRule(models.Model):
    keywords = models.JSONField(verbose_name='关键词列表')
    require_yolo_target = models.CharField(max_length=64, blank=True, null=True, verbose_name="需要YOLO目标")
    desc = models.CharField(max_length=256, verbose_name='规则描述')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.desc

    class Meta:
        verbose_name = "复核校验规则"
        verbose_name_plural = "复核校验规则"
