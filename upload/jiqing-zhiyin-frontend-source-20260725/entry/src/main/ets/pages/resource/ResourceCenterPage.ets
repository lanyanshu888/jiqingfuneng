import { ResourceCard } from '../../components/ResourceCard';
import { AppTheme } from '../../theme/AppTheme';
import { RESOURCES_FIXTURE } from '../../mock/MockFixtures';
import { GrowthResource, ResourceType } from '../../models/ResourceModels';

@Component
export struct ResourceCenterPage {
  @State selectedType: ResourceType = 'policy';
  @State keyword: string = '';
  @State resources: GrowthResource[] = RESOURCES_FIXTURE;
  @StorageLink('pendingResourceTab') pendingResourceTab: string = '';

  aboutToAppear(): void {
    const preset = this.pendingResourceTab as string;
    if (preset === 'policy' || preset === 'opportunity' || preset === 'course' || preset === 'activity' || preset === 'mentor') {
      this.selectedType = preset as ResourceType;
      AppStorage.setOrCreate<string>('pendingResourceTab', '');
    }
  }

  private typeLabel(type: ResourceType): string {
    if (type === 'policy') {
      return '政策';
    }
    if (type === 'opportunity') {
      return '岗位';
    }
    if (type === 'course') {
      return '课程';
    }
    if (type === 'activity') {
      return '活动';
    }
    return '导师';
  }

  private filtered(): GrowthResource[] {
    return this.resources.filter((item) => {
      const hitType = item.resourceType === this.selectedType;
      const hitKeyword = this.keyword.length === 0 || item.title.includes(this.keyword);
      return hitType && hitKeyword;
    });
  }

  build() {
    Column({ space: AppTheme.CARD_GAP }) {
      Text('资源中心')
        .fontSize(AppTheme.TITLE_SIZE)
        .fontWeight(FontWeight.Bold)
        .fontColor($r('app.color.text_primary'))
        .width('100%');
      TextInput({ placeholder: '搜索关键词', text: this.keyword })
        .onChange((value: string) => {
          this.keyword = value;
        });
      Row({ space: 6 }) {
        ForEach(['policy', 'opportunity', 'course', 'activity', 'mentor'], (type: ResourceType) => {
          Button(this.typeLabel(type))
            .backgroundColor(this.selectedType === type ? $r('app.color.primary') : $r('app.color.primary_light'))
            .fontColor(this.selectedType === type ? Color.White : $r('app.color.primary'))
            .layoutWeight(1)
            .onClick(() => {
              this.selectedType = type;
            });
        });
      }
      Scroll() {
        Column({ space: AppTheme.CARD_GAP }) {
          ForEach(this.filtered(), (resource: GrowthResource) => {
            ResourceCard({ resource });
          });
        }
      }
    }
    .padding(AppTheme.PAGE_PADDING)
    .backgroundColor($r('app.color.app_background'));
  }
}
