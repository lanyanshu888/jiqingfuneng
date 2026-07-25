import { router } from '@kit.ArkUI';
import { AppTheme } from '../../theme/AppTheme';
import { AuthRepository } from '../../repositories/AuthRepository';

@Entry
@Component
struct RegisterPage {
  @State username: string = '';
  @State nickname: string = '';
  @State password: string = '';
  @State confirmPassword: string = '';
  @State message: string = '';
  @State loading: boolean = false;
  private repository: AuthRepository = new AuthRepository();

  build() {
    Column({ space: 14 }) {
      Text('注册账号')
        .fontSize(AppTheme.TITLE_SIZE)
        .fontWeight(FontWeight.Bold)
        .width('100%');
      TextInput({ placeholder: '用户名', text: this.username })
        .onChange((value: string) => this.username = value)
        .enabled(!this.loading);
      TextInput({ placeholder: '昵称', text: this.nickname })
        .onChange((value: string) => this.nickname = value)
        .enabled(!this.loading);
      TextInput({ placeholder: '密码', text: this.password })
        .type(InputType.Password)
        .onChange((value: string) => this.password = value)
        .enabled(!this.loading);
      TextInput({ placeholder: '确认密码', text: this.confirmPassword })
        .type(InputType.Password)
        .onChange((value: string) => this.confirmPassword = value)
        .enabled(!this.loading);
      if (this.message.length > 0) {
        Text(this.message)
          .fontSize(AppTheme.BODY_SIZE)
          .fontColor($r('app.color.danger'))
          .width('100%');
      }
      Button(this.loading ? '注册中...' : '注册并登录')
        .width('100%')
        .backgroundColor($r('app.color.primary'))
        .enabled(!this.loading)
        .onClick(async () => {
          this.message = '';
          if (this.username.trim().length === 0) {
            this.message = '请输入用户名';
            return;
          }
          if (this.nickname.trim().length === 0) {
            this.message = '请输入昵称';
            return;
          }
          if (this.password.length === 0) {
            this.message = '请输入密码';
            return;
          }
          if (this.password !== this.confirmPassword) {
            this.message = '两次密码不一致';
            return;
          }
          this.loading = true;
          try {
            await this.repository.register({
              nickname: this.nickname.trim(),
              username: this.username.trim(),
              password: this.password
            });
            router.replaceUrl({ url: 'pages/Index' });
          } catch (error) {
            const msg = String(error);
            if (msg.includes('网络') || msg.includes('连接') || msg.includes('服务器')) {
              this.message = '无法连接服务器，请检查网络';
            } else if (msg.includes('已存在') || msg.includes('409')) {
              this.message = '用户名已存在';
            } else {
              this.message = msg.length > 50 ? '注册失败，请稍后重试' : msg;
            }
          } finally {
            this.loading = false;
          }
        });

      Row({ space: 4 }) {
        Text('已有账号？')
          .fontSize(AppTheme.BODY_SIZE)
          .fontColor($r('app.color.text_secondary'));
        Text('返回登录')
          .fontSize(AppTheme.BODY_SIZE)
          .fontColor($r('app.color.primary'))
          .fontWeight(FontWeight.Bold);
      }
      .width('100%')
      .justifyContent(FlexAlign.Center)
      .onClick(() => {
        router.back();
      });
    }
    .justifyContent(FlexAlign.Center)
    .padding(AppTheme.PAGE_PADDING)
    .backgroundColor($r('app.color.app_background'))
    .width('100%')
    .height('100%');
  }
}
