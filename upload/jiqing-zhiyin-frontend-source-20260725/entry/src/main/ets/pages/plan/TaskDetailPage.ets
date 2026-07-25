import { AppTheme } from '../../theme/AppTheme';
import { PLAN_FIXTURE } from '../../mock/MockFixtures';

@Entry
@Component
struct TaskDetailPage {
  build() {
    Column({ space: 12 }) {
      Text(PLAN_FIXTURE.todayTask.title)
        .fontSize(AppTheme.TITLE_SIZE)
        .fontWeight(FontWeight.Bold);
      Text(PLAN_FIXTURE.todayTask.description)
        .fontSize(AppTheme.BODY_SIZE)
        .fontColor($r('app.color.text_secondary'));
      Button('标记完成').backgroundColor($r('app.color.primary'));
    }
    .padding(AppTheme.PAGE_PADDING)
    .backgroundColor($r('app.color.app_background'));
  }
}

