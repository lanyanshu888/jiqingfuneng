import { AppTheme } from '../../theme/AppTheme';
import { AssistantResult } from '../../models/AssistantModels';
import { DAILY_SUGGESTION_FIXTURE } from '../../mock/MockFixtures';

@Component
export struct AssistantPage {
  @State result: AssistantResult = DAILY_SUGGESTION_FIXTURE;

  @Builder
  actionCard(title: string, summary: string, action: () => void) {
    Column({ space: 8 }) {
      Text(title)
        .fontSize(17)
        .fontWeight(FontWeight.Bold)
        .fontColor($r('app.color.text_primary'));
      Text(summary)
        .fontSize(AppTheme.BODY_SIZE)
        .fontColor($r('app.color.text_secondary'));
    }
    .alignItems(HorizontalAlign.Start)
    .padding(AppTheme.PAGE_PADDING)
    .width('100%')
    .backgroundColor($r('app.color.surface'))
    .borderRadius(AppTheme.CARD_RADIUS)
    .onClick(action);
  }

  build() {
    Scroll() {
      Column({ space: AppTheme.CARD_GAP }) {
        Text('智能助手')
          .fontSize(AppTheme.TITLE_SIZE)
          .fontWeight(FontWeight.Bold)
          .fontColor($r('app.color.text_primary'))
          .width('100%');
        Text(this.result.message)
          .fontSize(AppTheme.BODY_SIZE)
          .fontColor($r('app.color.text_secondary'))
          .width('100%');
        this.actionCard('画像分析', '基于你的资料生成成长画像', () => {
          this.result = {
            action: 'profile_analysis',
            title: '画像分析',
            message: '你当前更接近就业准备型，适合从县域数字运营切入。',
            cards: []
          };
        });
        this.actionCard('生成职业计划', '按目标生成 7 天、1 个月、3 个月行动建议', () => {
          this.result = {
            action: 'career_plan',
            title: '职业计划',
            message: '已按县域数字运营生成成长计划。',
            cards: []
          };
        });
        this.actionCard('政策搜索', '快速找到地区和关键词相关政策', () => {
          this.result = {
            action: 'policy_search',
            title: '政策搜索',
            message: '已找到高校毕业生就业相关政策。',
            cards: []
          };
        });
        this.actionCard('资源匹配', '匹配岗位、课程、活动和导师', () => {
          this.result = {
            action: 'resource_match',
            title: '资源匹配',
            message: '已匹配到适合你的成长资源。',
            cards: []
          };
        });
        this.actionCard('今日建议', '给出今天最值得完成的一件事', () => {
          this.result = DAILY_SUGGESTION_FIXTURE;
        });
      }
      .padding(AppTheme.PAGE_PADDING);
    }
    .backgroundColor($r('app.color.app_background'));
  }
}

