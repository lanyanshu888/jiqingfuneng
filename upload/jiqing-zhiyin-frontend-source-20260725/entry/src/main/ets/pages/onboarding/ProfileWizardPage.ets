import { AppTheme } from '../../theme/AppTheme';
import { ProfileRepository } from '../../repositories/ProfileRepository';

@Entry
@Component
struct ProfileWizardPage {
  @State goal: string = '';
  @State message: string = '';
  private repository: ProfileRepository = new ProfileRepository();

  build() {
    Column({ space: 14 }) {
      Text('完善青年画像')
        .fontSize(AppTheme.TITLE_SIZE)
        .fontWeight(FontWeight.Bold)
        .width('100%');
      TextInput({ placeholder: '你的成长目标', text: this.goal })
        .onChange((value: string) => this.goal = value);
      if (this.message.length > 0) {
        Text(this.message)
          .fontSize(AppTheme.BODY_SIZE)
          .fontColor($r('app.color.primary'))
          .width('100%');
      }
      Button('生成画像')
        .width('100%')
        .backgroundColor($r('app.color.primary'))
        .onClick(async () => {
          try {
            const result = await this.repository.saveMyProfile({
              summary: this.goal
            });
            this.message = '画像已保存';
          } catch (error) {
            const msg = String(error);
            this.message = msg.length > 50 ? '保存失败' : msg;
          }
        });
    }
    .padding(AppTheme.PAGE_PADDING)
    .backgroundColor($r('app.color.app_background'));
  }
}
