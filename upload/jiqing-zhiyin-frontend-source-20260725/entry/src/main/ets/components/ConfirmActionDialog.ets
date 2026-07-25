@Component
export struct ConfirmActionDialog {
  title: string = '';
  actionText: string = '';
  consequence: string = '';
  running: boolean = false;
  onCancel?: () => void;
  onConfirm?: () => void;

  build() {
    Column({ space: 12 }) {
      Text(this.title).fontSize(18).fontWeight(FontWeight.Bold);
      Text(this.consequence).fontSize(14).fontColor($r('app.color.text_secondary'));
      Row({ space: 12 }) {
        Button('取消')
          .backgroundColor($r('app.color.divider'))
          .fontColor($r('app.color.text_primary'))
          .layoutWeight(1)
          .onClick(() => {
            if (this.onCancel) {
              this.onCancel();
            }
          });
        Button(this.running ? '处理中' : this.actionText)
          .enabled(!this.running)
          .backgroundColor($r('app.color.primary'))
          .layoutWeight(1)
          .onClick(() => {
            if (this.onConfirm) {
              this.onConfirm();
            }
          });
      }
    }
    .padding(18)
    .backgroundColor($r('app.color.surface'))
    .borderRadius(12);
  }
}

