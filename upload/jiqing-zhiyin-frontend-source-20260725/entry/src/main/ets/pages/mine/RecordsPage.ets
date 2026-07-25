import { AppTheme } from '../../theme/AppTheme';
import { RECORDS_FIXTURE } from '../../mock/MockFixtures';

@Entry
@Component
struct RecordsPage {
  build() {
    Column({ space: 12 }) {
      Text('成长记录')
        .fontSize(AppTheme.TITLE_SIZE)
        .fontWeight(FontWeight.Bold);
      Text(`收藏 ${RECORDS_FIXTURE.favorites}`);
      Text(`申请 ${RECORDS_FIXTURE.applications}`);
      Text(`报名 ${RECORDS_FIXTURE.enrollments}`);
      Text(`完成课程 ${RECORDS_FIXTURE.completedCourses}`);
      Text(`导师咨询 ${RECORDS_FIXTURE.consultations}`);
    }
    .alignItems(HorizontalAlign.Start)
    .padding(AppTheme.PAGE_PADDING)
    .backgroundColor($r('app.color.app_background'));
  }
}

