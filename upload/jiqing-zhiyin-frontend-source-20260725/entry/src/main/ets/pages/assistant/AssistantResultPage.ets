import { AppTheme } from '../../theme/AppTheme';
import { DAILY_SUGGESTION_FIXTURE } from '../../mock/MockFixtures';
import { AssistantCard } from '../../models/AssistantModels';

@Entry
@Component
struct AssistantResultPage {
  build() {
    Scroll() {
      Column({ space: AppTheme.CARD_GAP }) {
        Text(DAILY_SUGGESTION_FIXTURE.title)
          .fontSize(AppTheme.TITLE_SIZE)
          .fontWeight(FontWeight.Bold)
          .fontColor($r('app.color.text_primary'));
        Text(DAILY_SUGGESTION_FIXTURE.message)
          .fontSize(AppTheme.BODY_SIZE)
          .fontColor($r('app.color.text_secondary'));
        ForEach(DAILY_SUGGESTION_FIXTURE.cards, (card: AssistantCard) => {
          Column({ space: 8 }) {
            Text(card.title).fontSize(17).fontWeight(FontWeight.Bold);
            Text(card.summary).fontSize(AppTheme.BODY_SIZE).fontColor($r('app.color.text_secondary'));
            ForEach(card.reasons, (reason: string) => {
              Text(reason).fontSize(AppTheme.CAPTION_SIZE).fontColor($r('app.color.primary'));
            });
          }
          .alignItems(HorizontalAlign.Start)
          .padding(AppTheme.PAGE_PADDING)
          .width('100%')
          .backgroundColor($r('app.color.surface'))
          .borderRadius(AppTheme.CARD_RADIUS);
        });
      }
      .padding(AppTheme.PAGE_PADDING);
    }
    .backgroundColor($r('app.color.app_background'));
  }
}

