import { router } from '@kit.ArkUI';
import { promptAction } from '@kit.ArkUI';
import { GrowthProgressCard } from '../../components/GrowthProgressCard';
import { AppTheme } from '../../theme/AppTheme';
import { DASHBOARD_FIXTURE, MOCK_USER } from '../../mock/MockFixtures';
import { authStore } from '../../core/auth/AuthStore';
import { DemoState } from '../../state/DemoState';

@CustomDialog
struct LogoutConfirmDialog {
  controller?: CustomDialogController;
  isDemo: boolean = false;

  build() {
    Column({ space: 12 }) {
      Text(this.isDemo ? '退出演示模式' : '确认退出')
        .fontSize(18).fontWeight(FontWeight.Bold);
      Text(this.isDemo ? '退出后将返回登录页，不会影响真实账号数据。' : '确定要退出当前账号吗？')
        .fontSize(14).fontColor($r('app.color.text_secondary'));
      Row({ space: 12 }) {
        Button('取消')
          .backgroundColor($r('app.color.divider'))
          .fontColor($r('app.color.text_primary'))
          .layoutWeight(1)
          .onClick(() => {
            if (this.controller) {
              this.controller.close();
            }
          });
        Button(this.isDemo ? '退出演示' : '确定退出')
          .backgroundColor($r('app.color.danger'))
          .layoutWeight(1)
          .onClick(async () => {
            if (this.controller) {
              this.controller.close();
            }
            if (this.isDemo) {
              DemoState.exit();
              router.replaceUrl({ url: 'pages/auth/LoginPage' });
            } else {
              await authStore.clear();
              router.replaceUrl({ url: 'pages/auth/LoginPage' });
            }
          });
      }
    }
    .padding(18);
  }
}

@Component
export struct MinePage {
  private isDemo: boolean = DemoState.isActive();

  aboutToAppear(): void {
    this.isDemo = DemoState.isActive();
  }

  build() {
    Scroll() {
      Column({ space: AppTheme.CARD_GAP }) {
        Text('我的')
          .fontSize(AppTheme.TITLE_SIZE)
          .fontWeight(FontWeight.Bold)
          .fontColor($r('app.color.text_primary'))
          .width('100%');

        if (this.isDemo) {
          Row() {
            Text('离线演示模式')
              .fontSize(13)
              .fontColor($r('app.color.primary'))
              .fontWeight(FontWeight.Bold);
          }
          .padding({ left: 12, right: 12, top: 6, bottom: 6 })
          .backgroundColor($r('app.color.primary_light'))
          .borderRadius(8);
        }

        Column({ space: 4 }) {
          Text(MOCK_USER.nickname)
            .fontSize(20)
            .fontWeight(FontWeight.Bold)
            .fontColor($r('app.color.text_primary'));
          Text(`当前目标：${DASHBOARD_FIXTURE.currentGoal}`)
            .fontSize(AppTheme.BODY_SIZE)
            .fontColor($r('app.color.text_secondary'));
        }
        .alignItems(HorizontalAlign.Start)
        .padding(AppTheme.PAGE_PADDING)
        .width('100%')
        .backgroundColor($r('app.color.surface'))
        .borderRadius(AppTheme.CARD_RADIUS);
        GrowthProgressCard({
          title: '个人成长',
          progress: DASHBOARD_FIXTURE.progress,
          summary: `画像完整度 ${DASHBOARD_FIXTURE.profileCompleteness}%`
        });

        Column() { this.menuItem('个人画像', '编辑资料和目标方向'); }
        .onClick(() => {
          promptAction.showToast({ message: '点击个人画像', duration: 1000 });
          router.pushUrl({ url: 'pages/mine/ProfilePage' });
        });

        Column() { this.menuItem('成长记录', '收藏、报名、课程和咨询'); }
        .onClick(() => {
          promptAction.showToast({ message: '点击成长记录', duration: 1000 });
          router.pushUrl({ url: 'pages/mine/RecordsPage' });
        });

        Column() { this.menuItem('提醒设置', '管理本地任务提醒'); }
        .onClick(() => {
          promptAction.showToast({ message: '点击提醒设置', duration: 1000 });
          router.pushUrl({ url: 'pages/mine/SettingsPage' });
        });

        Button(this.isDemo ? '退出演示模式' : '退出登录')
          .backgroundColor($r('app.color.danger'))
          .width('100%')
          .onClick(() => {
            promptAction.showToast({ message: this.isDemo ? '退出演示模式' : '点击退出登录', duration: 1000 });
            if (this.isDemo) {
              AlertDialog.show({
                title: '退出演示模式',
                message: '退出后将返回登录页，不会影响真实账号数据。',
                primaryButton: { value: '取消', action: () => {} },
                secondaryButton: {
                  value: '退出演示',
                  fontColor: $r('app.color.danger'),
                  action: () => {
                    DemoState.exit();
                    router.replaceUrl({ url: 'pages/auth/LoginPage' });
                  }
                }
              });
            } else {
              const dialogController = new CustomDialogController({
                builder: LogoutConfirmDialog({ isDemo: false }),
                autoCancel: true,
                alignment: DialogAlignment.Center
              });
              dialogController.open();
            }
          });
      }
      .padding(AppTheme.PAGE_PADDING);
    }
    .backgroundColor($r('app.color.app_background'));
  }

  @Builder
  menuItem(title: string, detail: string) {
    Row() {
      Column() {
        Text(title).fontSize(16).fontColor($r('app.color.text_primary'));
        Text(detail).fontSize(AppTheme.CAPTION_SIZE).fontColor($r('app.color.text_secondary'));
      }
      .alignItems(HorizontalAlign.Start)
      .layoutWeight(1);
      Text('>').fontColor($r('app.color.text_secondary'));
    }
    .padding(AppTheme.PAGE_PADDING)
    .width('100%')
    .backgroundColor($r('app.color.surface'))
    .borderRadius(AppTheme.CARD_RADIUS);
  }
}
