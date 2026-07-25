import { AssistantPage } from './assistant/AssistantPage';
import { HomePage } from './home/HomePage';
import { MinePage } from './mine/MinePage';
import { PlanPage } from './plan/PlanPage';
import { ResourceCenterPage } from './resource/ResourceCenterPage';

@Entry
@Component
struct Index {
  @State currentIndex: number = 0;

  build() {
    Tabs({ index: this.currentIndex, barPosition: BarPosition.End }) {
      TabContent() { HomePage() }.tabBar('首页')
      TabContent() { PlanPage() }.tabBar('规划')
      TabContent() { ResourceCenterPage() }.tabBar('资源')
      TabContent() { AssistantPage() }.tabBar('助手')
      TabContent() { MinePage() }.tabBar('我的')
    }
    .barMode(BarMode.Fixed)
    .onChange((index: number) => {
      this.currentIndex = index;
    })
    .backgroundColor($r('app.color.app_background'));
  }
}

