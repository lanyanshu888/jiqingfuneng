import { GrowthProgressCard } from '../../components/GrowthProgressCard';
import { AppTheme } from '../../theme/AppTheme';
import { DASHBOARD_FIXTURE, MOCK_USER } from '../../mock/MockFixtures';

@Component
export struct MinePage {
  @Builder
  menuItem(title: string, detail: string) {
    Row() {
      Column() {
        Text(title).fontSize(16).fontColor($r('app.color.text_primary'));
        Text(detail).fontSize(AppTheme.CAPTION_SIZE).fontColor($r('app.color.text_secondary'));
      }
      .alignItems(HorizontalAlign.Start)
      .layoutWeight(1);
      Text('>').fontColor($r('app.color.text_secondary'));
    }
    .padding(AppTheme.PAGE_PADDING)
    .width('100%')
    .backgroundColor($r('app.color.surface'))
    .borderRadius(AppTheme.CARD_RADIUS);
  }

  build() {
    Scroll() {
      Column({ space: AppTheme.CARD_GAP }) {
        Text('我的')
          .fontSize(AppTheme.TITLE_SIZE)
          .fontWeight(FontWeight.Bold)
          .fontColor($r('app.color.text_primary'))
          .width('100%');
        Column({ space: 4 }) {
          Text(MOCK_USER.nickname)
            .fontSize(20)
            .fontWeight(FontWeight.Bold)
            .fontColor($r('app.color.text_primary'));
          Text(`当前目标：${DASHBOARD_FIXTURE.currentGoal}`)
            .fontSize(AppTheme.BODY_SIZE)
            .fontColor($r('app.color.text_secondary'));
        }
        .alignItems(HorizontalAlign.Start)
        .padding(AppTheme.PAGE_PADDING)
        .width('100%')
        .backgroundColor($r('app.color.surface'))
        .borderRadius(AppTheme.CARD_RADIUS);
        GrowthProgressCard({
          title: '个人成长',
          progress: DASHBOARD_FIXTURE.progress,
          summary: `画像完整度 ${DASHBOARD_FIXTURE.profileCompleteness}%`
        });
        this.menuItem('个人画像', '编辑资料和目标方向');
        this.menuItem('成长记录', '收藏、报名、课程和咨询');
        this.menuItem('提醒设置', '管理本地任务提醒');
        Button('退出登录')
          .backgroundColor($r('app.color.danger'))
          .width('100%');
      }
      .padding(AppTheme.PAGE_PADDING);
    }
    .backgroundColor($r('app.color.app_background'));
  }
}

