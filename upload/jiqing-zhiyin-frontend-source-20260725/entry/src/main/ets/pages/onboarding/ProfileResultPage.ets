import { AppTheme } from '../../theme/AppTheme';
import { PROFILE_RESULT_FIXTURE } from '../../mock/MockFixtures';

@Entry
@Component
struct ProfileResultPage {
  build() {
    Column({ space: 12 }) {
      Text(PROFILE_RESULT_FIXTURE.title)
        .fontSize(AppTheme.TITLE_SIZE)
        .fontWeight(FontWeight.Bold);
      Text(PROFILE_RESULT_FIXTURE.summary)
        .fontSize(AppTheme.BODY_SIZE)
        .fontColor($r('app.color.text_secondary'));
      ForEach(PROFILE_RESULT_FIXTURE.suggestions, (item: string) => {
        Text(item).fontSize(AppTheme.BODY_SIZE).fontColor($r('app.color.primary'));
      });
      Button('进入首页').backgroundColor($r('app.color.primary'));
    }
    .alignItems(HorizontalAlign.Start)
    .padding(AppTheme.PAGE_PADDING)
    .backgroundColor($r('app.color.app_background'));
  }
}

