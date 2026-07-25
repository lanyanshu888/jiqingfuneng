import { AppTheme } from '../theme/AppTheme';

export type AsyncStatus = 'idle' | 'loading' | 'content' | 'empty' | 'error' | 'offline';

@Component
export struct AsyncStateView {
  status: AsyncStatus = 'content';
  title: string = '暂无内容';
  description: string = '';
  actionText: string = '';
  cachedAtText: string = '';
  onAction?: () => void;
  content?: () => void;

  @Builder
  renderMessage(message: string) {
    Column({ space: 10 }) {
      Text(this.title)
        .fontSize(AppTheme.SECTION_SIZE)
        .fontWeight(FontWeight.Bold)
        .fontColor($r('app.color.text_primary'));
      Text(message)
        .fontSize(AppTheme.BODY_SIZE)
        .fontColor($r('app.color.text_secondary'))
        .textAlign(TextAlign.Center);
      if (this.actionText.length > 0) {
        Button(this.actionText)
          .backgroundColor($r('app.color.primary'))
          .onClick(() => {
            if (this.onAction) {
              this.onAction();
            }
          });
      }
    }
    .width('100%')
    .padding(24)
    .backgroundColor($r('app.color.surface'))
    .borderRadius(AppTheme.CARD_RADIUS);
  }

  build() {
    Column() {
      if (this.status === 'loading') {
        LoadingProgress()
          .width(36)
          .height(36)
          .color($r('app.color.primary'));
        Text('正在加载')
          .fontColor($r('app.color.text_secondary'))
          .margin({ top: 8 });
      } else if (this.status === 'empty') {
        this.renderMessage(this.description.length > 0 ? this.description : '还没有可展示的信息');
      } else if (this.status === 'error') {
        this.renderMessage(this.description.length > 0 ? this.description : '加载失败，请稍后重试');
      } else if (this.status === 'offline') {
        this.renderMessage(`当前离线，正在显示最近保存的内容${this.cachedAtText.length > 0 ? ' · 更新于 ' + this.cachedAtText : ''}`);
      } else {
        if (this.content) {
          this.content();
        }
      }
    }
    .width('100%')
    .alignItems(HorizontalAlign.Center)
    .justifyContent(FlexAlign.Center);
  }
}

