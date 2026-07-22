from datetime import date, datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Activity, Course, Mentor, Opportunity, Policy


class Command(BaseCommand):
    help = "创建冀青赋能演示资源数据；可重复执行。"

    def handle(self, *args, **options):
        Policy.objects.update_or_create(
            title="高校毕业生就业见习补贴",
            defaults={
                "status": "published", "region": "沧州市", "category": "就业补贴",
                "target": "毕业两年内未就业高校毕业生、16-24岁失业青年",
                "support": "参加认定见习岗位可获得生活补贴和就业服务。",
                "conditions": ["完成实名登记", "参加认定见习岗位"],
                "materials": ["身份证", "毕业证或学籍证明", "见习协议"],
                "process": ["提交申请", "材料初审", "单位确认", "部门复核"],
                "location": "当地公共就业服务机构", "phone": "0317-1234567",
                "source": "河北省公共就业服务政策汇编", "published_at": date(2026, 4, 10),
                "effective_until": date(2026, 12, 31),
            },
        )
        Opportunity.objects.update_or_create(
            title="县域数字运营实习生",
            defaults={
                "status": "published", "type": "实习见习", "unit": "沧州科技服务有限公司",
                "region": "沧州黄骅市", "pay": "100元/天", "education": "本科及以上",
                "major": "计算机、电子商务、新闻传播相关", "deadline": date(2026, 12, 31),
                "tags": ["本地实习", "实习优先", "数字运营"],
                "detail": "参与县域企业新媒体账号维护、活动页面更新和基础数据整理。",
            },
        )
        Course.objects.update_or_create(
            title="县域青年面试表达训练",
            defaults={
                "status": "published", "category": "面试技巧", "target": "求职青年、职业院校学生",
                "duration": "45分钟", "teacher": "李经理", "goal": "掌握自我介绍和项目经历表达。",
                "materials": "面试题库、表达练习表", "certificate": True, "tags": ["就业准备", "面试"],
            },
        )
        Activity.objects.update_or_create(
            title="冀青赋能·县域大学生就业成长营",
            defaults={
                "status": "published", "starts_at": timezone.make_aware(datetime(2026, 8, 18, 9, 0)),
                "place": "黄骅市青年中心", "host": "项目团队、合作团委、学校就业部门",
                "target": "在校大学生、待就业青年、返乡发展青年", "capacity": 50,
                "agenda": ["政策解读", "简历门诊", "企业岗位对接", "导师答疑"],
                "tags": ["就业成长营", "线下活动", "导师答疑"],
            },
        )
        Mentor.objects.update_or_create(
            title="赵老师",
            defaults={"status": "published", "role": "创业导师", "good_at": "创业计划书、政策申请、项目孵化", "available": "周日 10:00-11:30"},
        )
        self.stdout.write(self.style.SUCCESS("演示资源数据已准备完成。"))
