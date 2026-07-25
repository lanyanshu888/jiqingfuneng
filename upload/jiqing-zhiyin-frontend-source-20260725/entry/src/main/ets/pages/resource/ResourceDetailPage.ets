import { AppTheme } from '../../theme/AppTheme';
import { RESOURCES_FIXTURE } from '../../mock/MockFixtures';

@Entry
@Component
struct ResourceDetailPage {
  private resource = RESOURCES_FIXTURE[0];

  build() {
    Scroll() {
      Column({ space: 12 }) {
        Text(this.resource.title)
          .fontSize(AppTheme.TITLE_SIZE)
          .fontWeight(FontWeight.Bold)
          .fontColor($r('app.color.text_primary'));
        if (this.resource.description) {
          Text(this.resource.description)
            .fontSize(AppTheme.BODY_SIZE)
            .fontColor($r('app.color.text_secondary'));
        }
        ForEach(this.resource.reasons, (reason: string) => {
          Text(`推荐理由：${reason}`)
            .fontSize(AppTheme.BODY_SIZE)
            .fontColor($r('app.color.primary'));
        });
        Button(this.resource.resourceType === 'policy' ? '打开官方来源' : '确认行动')
          .backgroundColor($r('app.color.primary'));
      }
      .padding(AppTheme.PAGE_PADDING)
      .alignItems(HorizontalAlign.Start);
    }
    .backgroundColor($r('app.color.app_background'));
  }
}

