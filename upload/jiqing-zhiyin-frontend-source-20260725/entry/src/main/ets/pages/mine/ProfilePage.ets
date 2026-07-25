import { AppTheme } from '../../theme/AppTheme';
import { PROFILE_FIXTURE } from '../../mock/MockFixtures';

@Entry
@Component
struct ProfilePage {
  build() {
    Column({ space: 12 }) {
      Text('个人画像')
        .fontSize(AppTheme.TITLE_SIZE)
        .fontWeight(FontWeight.Bold);
      Text(`地区：${PROFILE_FIXTURE.region}`);
      Text(`学历：${PROFILE_FIXTURE.education}`);
      Text(`专业：${PROFILE_FIXTURE.major}`);
      Text(`目标：${PROFILE_FIXTURE.goal}`);
      Button('保存画像').backgroundColor($r('app.color.primary'));
    }
    .alignItems(HorizontalAlign.Start)
    .padding(AppTheme.PAGE_PADDING)
    .backgroundColor($r('app.color.app_background'));
  }
}

