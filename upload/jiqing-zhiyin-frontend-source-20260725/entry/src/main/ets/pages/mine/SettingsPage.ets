import { AppTheme } from '../../theme/AppTheme';

@Entry
@Component
struct SettingsPage {
  @State taskReminder: boolean = true;
  @State activityReminder: boolean = true;
  @State deadlineReminder: boolean = true;
  @State reviewReminder: boolean = false;

  @Builder
  switchRow(title: string, value: boolean, onChange: (value: boolean) => void) {
    Row() {
      Text(title)
        .fontSize(16)
        .fontColor($r('app.color.text_primary'))
        .layoutWeight(1);
      Toggle({ type: ToggleType.Switch, isOn: value })
        .onChange(onChange);
    }
    .padding(AppTheme.PAGE_PADDING)
    .width('100%')
    .backgroundColor($r('app.color.surface'))
    .borderRadius(AppTheme.CARD_RADIUS);
  }

  build() {
    Column({ space: AppTheme.CARD_GAP }) {
      Text('提醒设置')
        .fontSize(AppTheme.TITLE_SIZE)
        .fontWeight(FontWeight.Bold)
        .width('100%');
      this.switchRow('每日任务提醒', this.taskReminder, (value: boolean) => this.taskReminder = value);
      this.switchRow('活动提醒', this.activityReminder, (value: boolean) => this.activityReminder = value);
      this.switchRow('机会截止提醒', this.deadlineReminder, (value: boolean) => this.deadlineReminder = value);
      this.switchRow('规划复盘提醒', this.reviewReminder, (value: boolean) => this.reviewReminder = value);
    }
    .padding(AppTheme.PAGE_PADDING)
    .backgroundColor($r('app.color.app_background'));
  }
}

