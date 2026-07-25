import { AppTheme } from '../../theme/AppTheme';
import { ProfileRepository } from '../../repositories/ProfileRepository';
import { PROFILE_FIXTURE } from '../../mock/MockFixtures';

@Entry
@Component
struct ProfileWizardPage {
  @State goal: string = '县域数字运营';
  @State message: string = '';
  private repository: ProfileRepository = new ProfileRepository();

  build() {
    Column({ space: 14 }) {
      Text('完善青年画像')
        .fontSize(AppTheme.TITLE_SIZE)
        .fontWeight(FontWeight.Bold)
        .width('100%');
      TextInput({ placeholder: '你的成长目标', text: this.goal })
        .onChange((value: string) => this.goal = value);
      if (this.message.length > 0) {
        Text(this.message)
          .fontSize(AppTheme.BODY_SIZE)
          .fontColor($r('app.color.primary'))
          .width('100%');
      }
      Button('生成画像')
        .width('100%')
        .backgroundColor($r('app.color.primary'))
        .onClick(async () => {
          const result = await this.repository.save({
            name: PROFILE_FIXTURE.name,
            region: PROFILE_FIXTURE.region,
            education: PROFILE_FIXTURE.education,
            major: PROFILE_FIXTURE.major,
            goal: this.goal
            ,
            skills: PROFILE_FIXTURE.skills,
            completeness: PROFILE_FIXTURE.completeness
          });
          this.message = result.summary;
        });
    }
    .padding(AppTheme.PAGE_PADDING)
    .backgroundColor($r('app.color.app_background'));
  }
}
