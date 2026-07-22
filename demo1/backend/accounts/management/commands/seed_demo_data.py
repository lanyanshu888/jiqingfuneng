import os
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Activity, Course, Mentor, Opportunity, Policy, YouthProfile


class Command(BaseCommand):
    help = "创建冀青赋能演示资源数据；可重复执行。"

    def handle(self, *args, **options):
        today = date.today()
        demo_password = os.environ.get("JIQING_DEMO_PASSWORD", "demo-youth-local-only")
        demo_user, _created = User.objects.update_or_create(
            username="demo_youth",
            defaults={"first_name": "小冀"},
        )
        demo_user.set_password(demo_password)
        demo_user.save(update_fields=["password", "first_name"])
        YouthProfile.objects.update_or_create(
            user=demo_user,
            defaults={
                "nickname": "小冀",
                "age": 22,
                "region": "河北省沧州市黄骅市",
                "education": "本科",
                "major": "电子商务",
                "status": "应届毕业生",
                "profile_type": "县域就业成长型",
                "intents": ["想找工作", "想提升技能", "想参加社会实践"],
                "abilities": ["沟通表达", "内容策划"],
                "tags": ["数字运营", "县域就业", "本地实习"],
                "summary": "希望在河北县域从事数字运营，并通过课程和实践积累经验。",
            },
        )
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
                "source": "河北省公共就业服务政策汇编", "published_at": today,
                "effective_until": today + timedelta(days=365),
            },
        )
        Opportunity.objects.update_or_create(
            title="县域数字运营实习生",
            defaults={
                "status": "published", "type": "实习见习", "unit": "沧州科技服务有限公司",
                "region": "沧州黄骅市", "pay": "100元/天", "education": "本科及以上",
                "major": "计算机、电子商务、新闻传播相关", "deadline": today + timedelta(days=180),
                "tags": ["本地实习", "实习优先", "数字运营"],
                "detail": "参与县域企业新媒体账号维护、活动页面更新和基础数据整理。",
            },
        )
        Course.objects.update_or_create(
            title="县域青年数字运营与面试训练",
            defaults={
                "status": "published", "category": "数字运营", "target": "求职青年、电子商务专业学生",
                "duration": "60分钟", "teacher": "李经理", "goal": "掌握数字内容运营和项目经历表达。",
                "materials": "运营任务表、面试题库", "certificate": True, "tags": ["数字运营", "就业准备"],
            },
        )
        Activity.objects.update_or_create(
            title="冀青赋能·县域大学生就业成长营",
            defaults={
                "status": "published", "starts_at": timezone.now() + timedelta(days=30),
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
