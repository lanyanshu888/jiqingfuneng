import { router } from '@kit.ArkUI';
import { AssistantPage } from './assistant/AssistantPage';
import { HomePage } from './home/HomePage';
import { MinePage } from './mine/MinePage';
import { PlanPage } from './plan/PlanPage';
import { ResourceCenterPage } from './resource/ResourceCenterPage';
import { appState } from '../state/AppState';
import { DemoState } from '../state/DemoState';

@Entry
@Component
struct Index {
  @State currentIndex: number = 0;
  @State ready: boolean = false;
  @StorageLink('pendingTabIndex') pendingTabIndex: number = -1;

  async aboutToAppear(): Promise<void> {
    AppStorage.setOrCreate<number>('pendingTabIndex', -1);
    AppStorage.setOrCreate<string>('pendingResourceTab', '');
    await DemoState.waitReady();
    if (DemoState.isActive()) {
      this.ready = true;
      return;
    }
    const loggedIn = await appState.bootstrap();
    if (!loggedIn) {
      router.replaceUrl({ url: 'pages/auth/LoginPage' });
      return;
    }
    this.ready = true;
  }

  build() {
    if (!this.ready) {
      Column() {}.width('100%').height('100%').backgroundColor($r('app.color.app_background'));
    } else {
      Tabs({ index: this.pendingTabIndex >= 0 ? this.pendingTabIndex : this.currentIndex, barPosition: BarPosition.End }) {
        TabContent() { HomePage() }.tabBar('首页')
        TabContent() { PlanPage() }.tabBar('规划')
        TabContent() { ResourceCenterPage() }.tabBar('资源')
        TabContent() { AssistantPage() }.tabBar('助手')
        TabContent() { MinePage() }.tabBar('我的')
      }
      .barMode(BarMode.Fixed)
      .onChange((index: number) => {
        this.currentIndex = index;
        if (this.pendingTabIndex >= 0) {
          AppStorage.setOrCreate<number>('pendingTabIndex', -1);
        }
      })
      .backgroundColor($r('app.color.app_background'));
    }
  }
}
