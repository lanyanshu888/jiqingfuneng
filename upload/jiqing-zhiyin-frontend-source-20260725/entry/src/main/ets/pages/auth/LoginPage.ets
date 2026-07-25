import { AppTheme } from '../../theme/AppTheme';
import { appState } from '../../state/AppState';

@Entry
@Component
struct LoginPage {
  @State username: string = '';
  @State password: string = '';
  @State message: string = '';

  build() {
    Column({ space: 14 }) {
      Text('登录冀青智引')
        .fontSize(AppTheme.TITLE_SIZE)
        .fontWeight(FontWeight.Bold)
        .width('100%');
      TextInput({ placeholder: '用户名', text: this.username })
        .onChange((value: string) => this.username = value);
      TextInput({ placeholder: '密码', text: this.password })
        .type(InputType.Password)
        .onChange((value: string) => this.password = value);
      if (this.message.length > 0) {
        Text(this.message)
          .fontSize(AppTheme.BODY_SIZE)
          .fontColor($r('app.color.primary'))
          .width('100%');
      }
      Button('登录')
        .width('100%')
        .backgroundColor($r('app.color.primary'))
        .onClick(async () => {
          await appState.login(this.username, this.password);
          this.message = '登录成功，可以进入首页查看成长计划';
        });
    }
    .justifyContent(FlexAlign.Center)
    .padding(AppTheme.PAGE_PADDING)
    .backgroundColor($r('app.color.app_background'));
  }
}
