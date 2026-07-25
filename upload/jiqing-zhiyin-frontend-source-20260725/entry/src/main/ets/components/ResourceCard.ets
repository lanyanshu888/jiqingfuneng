import { AppTheme } from '../theme/AppTheme';
import { GrowthResource } from '../models/ResourceModels';

@Component
export struct ResourceCard {
  resource: GrowthResource = {
    id: 0,
    resourceType: 'policy',
    title: '',
    tags: [],
    reasons: [],
    favorited: false
  };
  onOpen?: (resource: GrowthResource) => void;

  build() {
    Column({ space: 8 }) {
      Row() {
        Text(this.resource.title)
          .fontSize(16)
          .fontWeight(FontWeight.Bold)
          .fontColor($r('app.color.text_primary'))
          .maxLines(2)
          .textOverflow({ overflow: TextOverflow.Ellipsis })
          .layoutWeight(1);
        Text(this.resource.favorited ? '已收藏' : '收藏')
          .fontSize(AppTheme.CAPTION_SIZE)
          .fontColor(this.resource.favorited ? $r('app.color.accent') : $r('app.color.text_secondary'));
      }
      if (this.resource.description) {
        Text(this.resource.description)
          .fontSize(AppTheme.BODY_SIZE)
          .fontColor($r('app.color.text_secondary'))
          .maxLines(2)
          .textOverflow({ overflow: TextOverflow.Ellipsis });
      }
      Row({ space: 8 }) {
        ForEach(this.resource.tags, (tag: string) => {
          Text(tag)
            .fontSize(AppTheme.CAPTION_SIZE)
            .fontColor($r('app.color.primary'))
            .padding({ left: 8, right: 8, top: 4, bottom: 4 })
            .backgroundColor($r('app.color.primary_light'))
            .borderRadius(8);
        });
      }
    }
    .alignItems(HorizontalAlign.Start)
    .padding(AppTheme.PAGE_PADDING)
    .width('100%')
    .backgroundColor($r('app.color.surface'))
    .borderRadius(AppTheme.CARD_RADIUS)
    .onClick(() => {
      if (this.onOpen) {
        this.onOpen(this.resource);
      }
    });
  }
}
