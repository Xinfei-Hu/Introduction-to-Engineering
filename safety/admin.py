from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import DetectionTask, SafetyRule, ReviewVerifyRule

@admin.register(SafetyRule)
class SafetyRuleAdmin(admin.ModelAdmin):
    list_display = ["rule_key", "rule_text", "updated_at"]
    search_fields = ["rule_key"]

@admin.register(ReviewVerifyRule)
class ReviewVerifyRuleAdmin(admin.ModelAdmin):
    list_display = ["desc", "require_yolo_target", "updated_at"]

@admin.register(DetectionTask)
class DetectionTaskAdmin(admin.ModelAdmin):
    list_display = ["task_id", "task_type", "status", "created_at"]