@Entry
@Component
struct GrowthCard {
  @LocalStorageProp('taskTitle') taskTitle: string = '登录冀青智引，查看今日成长任务';
  @LocalStorageProp('progress') progress: number = 0;
  @LocalStorageProp('deadlineText') deadlineText: string = '';

  build() {
    Column({ space: 8 }) {
      Text('冀青智引')
        .fontSize(16)
        .fontWeight(FontWeight.Bold)
        .fontColor('#17312F')
        .width('100%');
      Text(this.taskTitle)
        .fontSize(14)
        .fontColor('#17312F')
        .maxLines(2)
        .textOverflow({ overflow: TextOverflow.Ellipsis })
        .width('100%');
      Progress({ value: this.progress, total: 100, type: ProgressType.Linear })
        .color('#167D74')
        .backgroundColor('#DDF3EF')
        .height(6);
      Text(this.deadlineText.length > 0 ? this.deadlineText : '打开应用继续成长')
        .fontSize(12)
        .fontColor('#607572')
        .width('100%');
    }
    .padding(14)
    .width('100%')
    .height('100%')
    .backgroundColor('#F7FAF8');
  }
}

