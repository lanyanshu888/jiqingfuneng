import { router } from '@kit.ArkUI';
import { promptAction } from '@kit.ArkUI';
import { AppTheme } from '../../theme/AppTheme';
import { appState } from '../../state/AppState';
import { DemoState } from '../../state/DemoState';

@Entry
@Component
struct LoginPage {
  @State username: string = '';
  @State password: string = '';
  @State message: string = '';
  @State loading: boolean = false;

  build() {
    Column({ space: 14 }) {
      Text('登录冀青智引')
        .fontSize(AppTheme.TITLE_SIZE)
        .fontWeight(FontWeight.Bold)
        .width('100%');
      TextInput({ placeholder: '用户名', text: this.username })
        .onChange((value: string) => this.username = value)
        .enabled(!this.loading);
      TextInput({ placeholder: '密码', text: this.password })
        .type(InputType.Password)
        .onChange((value: string) => this.password = value)
        .enabled(!this.loading);
      if (this.message.length > 0) {
        Text(this.message)
          .fontSize(AppTheme.BODY_SIZE)
          .fontColor($r('app.color.danger'))
          .width('100%');
      }
      Button(this.loading ? '登录中...' : '登录')
        .width('100%')
        .backgroundColor($r('app.color.primary'))
        .enabled(!this.loading)
        .onClick(async () => {
          this.message = '';
          if (this.username.trim().length === 0) {
            this.message = '请输入用户名';
            return;
          }
          if (this.password.length === 0) {
            this.message = '请输入密码';
            return;
          }
          this.loading = true;
          try {
            await appState.login(this.username.trim(), this.password);
            router.replaceUrl({ url: 'pages/Index' });
          } catch (error) {
            const msg = String(error);
            if (msg.includes('网络') || msg.includes('连接') || msg.includes('服务器')) {
              this.message = '无法连接服务器，请检查网络或进入演示模式';
            } else if (msg.includes('401') || msg.includes('密码') || msg.includes('用户')) {
              this.message = '用户名或密码错误';
            } else {
              this.message = msg.length > 50 ? '登录失败，请稍后重试' : msg;
            }
          } finally {
            this.loading = false;
          }
        });

      Row({ space: 4 }) {
        Text('没有账号？')
          .fontSize(AppTheme.BODY_SIZE)
          .fontColor($r('app.color.text_secondary'));
        Text('立即注册')
          .fontSize(AppTheme.BODY_SIZE)
          .fontColor($r('app.color.primary'))
          .fontWeight(FontWeight.Bold);
      }
      .width('100%')
      .justifyContent(FlexAlign.Center)
      .onClick(() => {
        router.pushUrl({ url: 'pages/auth/RegisterPage' });
      });

      Button('进入演示模式')
        .width('100%')
        .backgroundColor($r('app.color.primary_light'))
        .fontColor($r('app.color.primary'))
        .onClick(() => {
          AlertDialog.show({
            title: '进入离线演示',
            message: '演示模式使用本地示例数据，不会连接服务器，也不会保存为真实账号数据。',
            primaryButton: {
              value: '取消',
              action: () => {}
            },
            secondaryButton: {
              value: '进入演示',
              fontColor: $r('app.color.primary'),
              action: () => {
                DemoState.enter();
                promptAction.showToast({ message: '已进入离线演示模式', duration: 1500 });
                router.replaceUrl({ url: 'pages/Index' });
              }
            }
          });
        });
    }
    .justifyContent(FlexAlign.Center)
    .padding(AppTheme.PAGE_PADDING)
    .backgroundColor($r('app.color.app_background'))
    .width('100%')
    .height('100%');
  }
}
