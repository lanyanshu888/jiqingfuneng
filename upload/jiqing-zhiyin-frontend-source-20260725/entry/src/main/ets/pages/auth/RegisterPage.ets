import { AppTheme } from '../../theme/AppTheme';
import { AuthRepository } from '../../repositories/AuthRepository';

@Entry
@Component
struct RegisterPage {
  @State nickname: string = '';
  @State username: string = '';
  @State password: string = '';
  @State message: string = '';
  private repository: AuthRepository = new AuthRepository();

  build() {
    Column({ space: 14 }) {
      Text('注册账号')
        .fontSize(AppTheme.TITLE_SIZE)
        .fontWeight(FontWeight.Bold)
        .width('100%');
      TextInput({ placeholder: '昵称', text: this.nickname })
        .onChange((value: string) => this.nickname = value);
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
      Button('注册并登录')
        .width('100%')
        .backgroundColor($r('app.color.primary'))
        .onClick(async () => {
          await this.repository.register({
            nickname: this.nickname,
            username: this.username,
            password: this.password
          });
          this.message = '注册成功，请继续完善青年画像';
        });
    }
    .justifyContent(FlexAlign.Center)
    .padding(AppTheme.PAGE_PADDING)
    .backgroundColor($r('app.color.app_background'));
  }
}
