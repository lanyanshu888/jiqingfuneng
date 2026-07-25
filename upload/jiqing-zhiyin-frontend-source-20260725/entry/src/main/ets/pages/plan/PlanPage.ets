import { AppTheme } from '../../theme/AppTheme';
import { PLAN_FIXTURE } from '../../mock/MockFixtures';
import { GrowthTask } from '../../models/PlanModels';

@Component
export struct PlanPage {
  @State selectedStage: string = '7days';
  @State tasks: GrowthTask[] = PLAN_FIXTURE.tasks;

  private stageTitle(stage: string): string {
    if (stage === '7days') {
      return '7 天';
    }
    if (stage === '1month') {
      return '1 个月';
    }
    return '3 个月';
  }

  build() {
    Column({ space: AppTheme.CARD_GAP }) {
      Text('成长规划')
        .fontSize(AppTheme.TITLE_SIZE)
        .fontWeight(FontWeight.Bold)
        .fontColor($r('app.color.text_primary'))
        .width('100%');
      Row({ space: 8 }) {
        ForEach(['7days', '1month', '3months'], (stage: string) => {
          Button(this.stageTitle(stage))
            .backgroundColor(this.selectedStage === stage ? $r('app.color.primary') : $r('app.color.primary_light'))
            .fontColor(this.selectedStage === stage ? Color.White : $r('app.color.primary'))
            .layoutWeight(1)
            .onClick(() => {
              this.selectedStage = stage;
            });
        });
      }
      Scroll() {
        Column({ space: AppTheme.CARD_GAP }) {
          ForEach(this.tasks.filter((task) => task.stage === this.selectedStage), (task: GrowthTask) => {
            Column({ space: 8 }) {
              Text(task.title)
                .fontSize(17)
                .fontWeight(FontWeight.Bold)
                .fontColor($r('app.color.text_primary'));
              Text(task.description)
                .fontSize(AppTheme.BODY_SIZE)
                .fontColor($r('app.color.text_secondary'));
              Row() {
                Text(task.deadlineText)
                  .fontSize(AppTheme.CAPTION_SIZE)
                  .fontColor($r('app.color.accent'))
                  .layoutWeight(1);
                Button(task.completed ? '已完成' : '完成')
                  .enabled(!task.completed)
                  .backgroundColor(task.completed ? $r('app.color.divider') : $r('app.color.primary'))
                  .onClick(() => {
                    this.tasks = this.tasks.map((item) => {
                      if (item.id === task.id) {
                        return {
                          id: item.id,
                          title: item.title,
                          description: item.description,
                          stage: item.stage,
                          deadlineText: item.deadlineText,
                          completed: true
                        };
                      }
                      return item;
                    });
                  });
              }
            }
            .alignItems(HorizontalAlign.Start)
            .padding(AppTheme.PAGE_PADDING)
            .width('100%')
            .backgroundColor($r('app.color.surface'))
            .borderRadius(AppTheme.CARD_RADIUS);
          });
        }
      }
    }
    .padding(AppTheme.PAGE_PADDING)
    .backgroundColor($r('app.color.app_background'));
  }
}
