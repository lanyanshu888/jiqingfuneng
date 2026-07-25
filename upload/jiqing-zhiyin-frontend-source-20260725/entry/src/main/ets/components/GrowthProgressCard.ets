import { AppTheme } from '../theme/AppTheme';

@Component
export struct GrowthProgressCard {
  title: string = '成长进度';
  progress: number = 0;
  summary: string = '';

  build() {
    Column({ space: 10 }) {
      Row() {
        Text(this.title)
          .fontSize(AppTheme.SECTION_SIZE)
          .fontWeight(FontWeight.Bold)
          .fontColor($r('app.color.text_primary'))
          .layoutWeight(1);
        Text(`${Math.round(this.progress)}%`)
          .fontSize(20)
          .fontWeight(FontWeight.Bold)
          .fontColor($r('app.color.primary'));
      }
      Progress({ value: this.progress, total: 100, type: ProgressType.Linear })
        .color($r('app.color.primary'))
        .backgroundColor($r('app.color.primary_light'))
        .height(8);
      Text(this.summary)
        .fontSize(AppTheme.BODY_SIZE)
        .fontColor($r('app.color.text_secondary'));
    }
    .padding(AppTheme.PAGE_PADDING)
    .width('100%')
    .backgroundColor($r('app.color.surface'))
    .borderRadius(AppTheme.CARD_RADIUS);
  }
}

