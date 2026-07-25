import { router } from '@kit.ArkUI';
import { promptAction } from '@kit.ArkUI';
import { AppTheme } from '../../theme/AppTheme';
import { AssistantResult } from '../../models/AssistantModels';
import { DAILY_SUGGESTION_FIXTURE } from '../../mock/MockFixtures';

@Component
export struct AssistantPage {
  @State result: AssistantResult = DAILY_SUGGESTION_FIXTURE;

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

        // 画像分析
        Column({ space: 8 }) {
          Text('画像分析')
            .fontSize(17)
            .fontWeight(FontWeight.Bold)
            .fontColor($r('app.color.text_primary'));
          Text('基于你的资料生成成长画像')
            .fontSize(AppTheme.BODY_SIZE)
            .fontColor($r('app.color.text_secondary'));
        }
        .alignItems(HorizontalAlign.Start)
        .padding(AppTheme.PAGE_PADDING)
        .width('100%')
        .backgroundColor($r('app.color.surface'))
        .borderRadius(AppTheme.CARD_RADIUS)
        .hitTestBehavior(HitTestMode.Block)
        .onClick(() => {
          promptAction.showToast({ message: '点击画像分析', duration: 1000 });
          router.pushUrl({ url: 'pages/mine/ProfilePage' });
        });

        // 生成职业计划
        Column({ space: 8 }) {
          Text('生成职业计划')
            .fontSize(17)
            .fontWeight(FontWeight.Bold)
            .fontColor($r('app.color.text_primary'));
          Text('按目标生成 7 天、1 个月、3 个月行动建议')
            .fontSize(AppTheme.BODY_SIZE)
            .fontColor($r('app.color.text_secondary'));
        }
        .alignItems(HorizontalAlign.Start)
        .padding(AppTheme.PAGE_PADDING)
        .width('100%')
        .backgroundColor($r('app.color.surface'))
        .borderRadius(AppTheme.CARD_RADIUS)
        .hitTestBehavior(HitTestMode.Block)
        .onClick(() => {
          promptAction.showToast({ message: '点击职业计划', duration: 1000 });
          AppStorage.setOrCreate<number>('pendingTabIndex', 1);
        });

        // 政策搜索
        Column({ space: 8 }) {
          Text('政策搜索')
            .fontSize(17)
            .fontWeight(FontWeight.Bold)
            .fontColor($r('app.color.text_primary'));
          Text('快速找到地区和关键词相关政策')
            .fontSize(AppTheme.BODY_SIZE)
            .fontColor($r('app.color.text_secondary'));
        }
        .alignItems(HorizontalAlign.Start)
        .padding(AppTheme.PAGE_PADDING)
        .width('100%')
        .backgroundColor($r('app.color.surface'))
        .borderRadius(AppTheme.CARD_RADIUS)
        .hitTestBehavior(HitTestMode.Block)
        .onClick(() => {
          promptAction.showToast({ message: '点击政策搜索', duration: 1000 });
          AppStorage.setOrCreate<string>('pendingResourceTab', 'policy');
          AppStorage.setOrCreate<number>('pendingTabIndex', 2);
        });

        // 资源匹配
        Column({ space: 8 }) {
          Text('资源匹配')
            .fontSize(17)
            .fontWeight(FontWeight.Bold)
            .fontColor($r('app.color.text_primary'));
          Text('匹配岗位、课程、活动和导师')
            .fontSize(AppTheme.BODY_SIZE)
            .fontColor($r('app.color.text_secondary'));
        }
        .alignItems(HorizontalAlign.Start)
        .padding(AppTheme.PAGE_PADDING)
        .width('100%')
        .backgroundColor($r('app.color.surface'))
        .borderRadius(AppTheme.CARD_RADIUS)
        .hitTestBehavior(HitTestMode.Block)
        .onClick(() => {
          promptAction.showToast({ message: '点击资源匹配', duration: 1000 });
          AppStorage.setOrCreate<number>('pendingTabIndex', 2);
        });

        // 今日建议
        Column({ space: 8 }) {
          Text('今日建议')
            .fontSize(17)
            .fontWeight(FontWeight.Bold)
            .fontColor($r('app.color.text_primary'));
          Text('给出今天最值得完成的一件事')
            .fontSize(AppTheme.BODY_SIZE)
            .fontColor($r('app.color.text_secondary'));
        }
        .alignItems(HorizontalAlign.Start)
        .padding(AppTheme.PAGE_PADDING)
        .width('100%')
        .backgroundColor($r('app.color.surface'))
        .borderRadius(AppTheme.CARD_RADIUS)
        .hitTestBehavior(HitTestMode.Block)
        .onClick(() => {
          promptAction.showToast({ message: '点击今日建议', duration: 1000 });
          router.pushUrl({ url: 'pages/assistant/AssistantResultPage' });
        });
      }
      .padding(AppTheme.PAGE_PADDING);
    }
    .backgroundColor($r('app.color.app_background'));
  }
}
