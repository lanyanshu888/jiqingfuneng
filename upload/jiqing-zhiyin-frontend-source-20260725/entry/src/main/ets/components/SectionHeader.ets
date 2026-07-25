import { AppTheme } from '../theme/AppTheme';

@Component
export struct SectionHeader {
  title: string = '';
  actionText: string = '';
  onAction?: () => void;

  build() {
    Row() {
      Text(this.title)
        .fontSize(AppTheme.SECTION_SIZE)
        .fontWeight(FontWeight.Bold)
        .fontColor($r('app.color.text_primary'))
        .layoutWeight(1);

      if (this.actionText.length > 0) {
        Button(this.actionText)
          .fontSize(AppTheme.CAPTION_SIZE)
          .fontColor($r('app.color.primary'))
          .backgroundColor(Color.Transparent)
          .onClick(() => {
            if (this.onAction) {
              this.onAction();
            }
          });
      }
    }
    .width('100%')
    .padding({ top: 6, bottom: 6 });
  }
}

