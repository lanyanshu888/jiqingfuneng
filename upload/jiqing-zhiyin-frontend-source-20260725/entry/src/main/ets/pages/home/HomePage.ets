import { GrowthProgressCard } from '../../components/GrowthProgressCard';
import { SectionHeader } from '../../components/SectionHeader';
import { AppTheme } from '../../theme/AppTheme';
import { DashboardResponse } from '../../models/PlanModels';
import { DASHBOARD_FIXTURE } from '../../mock/MockFixtures';

@Component
export struct HomePage {
  @State dashboard: DashboardResponse = DASHBOARD_FIXTURE;

  build() {
    Scroll() {
      Column({ space: AppTheme.CARD_GAP }) {
        Text(`你好，${this.dashboard.nickname}`)
          .fontSize(AppTheme.TITLE_SIZE)
          .fontWeight(FontWeight.Bold)
          .fontColor($r('app.color.text_primary'))
          .width('100%');
        Text(this.dashboard.suggestion)
          .fontSize(AppTheme.BODY_SIZE)
          .fontColor($r('app.color.text_secondary'))
          .width('100%');
        GrowthProgressCard({
          title: this.dashboard.currentGoal,
          progress: this.dashboard.progress,
          summary: `画像完整度 ${this.dashboard.profileCompleteness}%`
        });
        SectionHeader({ title: '今日任务' });
        Column({ space: 8 }) {
          Text(this.dashboard.plan.todayTask.title)
            .fontSize(18)
            .fontWeight(FontWeight.Bold)
            .fontColor($r('app.color.text_primary'));
          Text(this.dashboard.plan.todayTask.description)
            .fontSize(AppTheme.BODY_SIZE)
            .fontColor($r('app.color.text_secondary'));
          Text(this.dashboard.plan.todayTask.deadlineText)
            .fontSize(AppTheme.CAPTION_SIZE)
            .fontColor($r('app.color.accent'));
        }
        .alignItems(HorizontalAlign.Start)
        .padding(AppTheme.PAGE_PADDING)
        .width('100%')
        .backgroundColor($r('app.color.surface'))
        .borderRadius(AppTheme.CARD_RADIUS);
      }
      .padding(AppTheme.PAGE_PADDING);
    }
    .backgroundColor($r('app.color.app_background'));
  }
}

