import { router } from '@kit.ArkUI';
import { AppTheme } from '../../theme/AppTheme';
import { BackendProfile } from '../../models/ProfileModels';
import { ProfileRepository } from '../../repositories/ProfileRepository';
import { authStore } from '../../core/auth/AuthStore';

@Entry
@Component
struct ProfilePage {
  @State profile: BackendProfile | null = null;
  @State loading: boolean = true;
  @State saving: boolean = false;
  @State message: string = '';
  @State editRegion: string = '';
  @State editEducation: string = '';
  @State editMajor: string = '';
  @State editStatus: string = '';
  @State editIntents: string = '';
  @State editAbilities: string = '';
  @State editSummary: string = '';
  @State isEditing: boolean = false;
  private repository: ProfileRepository = new ProfileRepository();

  async aboutToAppear(): Promise<void> {
    await this.loadProfile();
  }

  async loadProfile(): Promise<void> {
    this.loading = true;
    this.message = '';
    try {
      const data = await this.repository.getMyProfile();
      this.profile = data;
      this.syncEditsFromProfile(data);
    } catch (error) {
      const msg = String(error);
      if (msg.includes('401')) {
        this.message = '登录已过期，请重新登录';
        await authStore.clear();
        router.replaceUrl({ url: 'pages/auth/LoginPage' });
      } else if (msg.includes('网络') || msg.includes('连接') || msg.includes('超时')) {
        this.message = '无法连接服务器，请稍后重试';
      } else {
        this.message = '加载失败，请返回重试';
      }
    } finally {
      this.loading = false;
    }
  }

  syncEditsFromProfile(p: BackendProfile): void {
    this.editRegion = p.region;
    this.editEducation = p.education;
    this.editMajor = p.major;
    this.editStatus = p.status;
    this.editIntents = p.intents.join('、');
    this.editAbilities = p.abilities.join('、');
    this.editSummary = p.summary;
  }

  async saveProfile(): Promise<void> {
    if (this.saving) {
      return;
    }
    this.saving = true;
    this.message = '';
    try {
      const intentsArr = this.editIntents.split('、').filter((s: string) => s.trim().length > 0);
      const abilitiesArr = this.editAbilities.split('、').filter((s: string) => s.trim().length > 0);
      const data = await this.repository.saveMyProfile({
        region: this.editRegion,
        education: this.editEducation,
        major: this.editMajor,
        status: this.editStatus,
        intents: intentsArr,
        abilities: abilitiesArr,
        summary: this.editSummary
      });
      this.profile = data;
      this.syncEditsFromProfile(data);
      this.message = '画像保存成功';
      this.isEditing = false;
    } catch (error) {
      const msg = String(error);
      if (msg.includes('401')) {
        this.message = '登录已过期，请重新登录';
        await authStore.clear();
        router.replaceUrl({ url: 'pages/auth/LoginPage' });
      } else if (msg.includes('网络') || msg.includes('连接') || msg.includes('超时')) {
        this.message = '无法连接服务器，请稍后重试';
      } else {
        this.message = msg.length > 50 ? '保存失败，请稍后重试' : msg;
      }
    } finally {
      this.saving = false;
    }
  }

  build() {
    Scroll() {
      Column({ space: AppTheme.CARD_GAP }) {
        Text('个人画像')
          .fontSize(AppTheme.TITLE_SIZE)
          .fontWeight(FontWeight.Bold)
          .fontColor($r('app.color.text_primary'))
          .width('100%');

        if (this.loading) {
          Text('加载中...')
            .fontSize(AppTheme.BODY_SIZE)
            .fontColor($r('app.color.text_secondary'));
        } else if (this.profile === null && this.message.length > 0) {
          Column({ space: 12 }) {
            Text(this.message)
              .fontSize(AppTheme.BODY_SIZE)
              .fontColor($r('app.color.danger'));
            Button('重新加载')
              .backgroundColor($r('app.color.primary'))
              .onClick(() => this.loadProfile());
          };
        } else if (this.profile !== null) {
          if (this.isEditing) {
            // 编辑模式
            Column({ space: 12 }) {
              Text('地区').fontSize(AppTheme.CAPTION_SIZE).fontColor($r('app.color.text_secondary'));
              TextInput({ placeholder: '请输入地区', text: this.editRegion })
                .onChange((v: string) => this.editRegion = v);
              Text('学历').fontSize(AppTheme.CAPTION_SIZE).fontColor($r('app.color.text_secondary'));
              TextInput({ placeholder: '请输入学历', text: this.editEducation })
                .onChange((v: string) => this.editEducation = v);
              Text('专业').fontSize(AppTheme.CAPTION_SIZE).fontColor($r('app.color.text_secondary'));
              TextInput({ placeholder: '请输入专业', text: this.editMajor })
                .onChange((v: string) => this.editMajor = v);
              Text('当前状态').fontSize(AppTheme.CAPTION_SIZE).fontColor($r('app.color.text_secondary'));
              TextInput({ placeholder: '请输入状态', text: this.editStatus })
                .onChange((v: string) => this.editStatus = v);
              Text('意向（用顿号分隔）').fontSize(AppTheme.CAPTION_SIZE).fontColor($r('app.color.text_secondary'));
              TextInput({ placeholder: '想找工作、想提升技能', text: this.editIntents })
                .onChange((v: string) => this.editIntents = v);
              Text('能力（用顿号分隔）').fontSize(AppTheme.CAPTION_SIZE).fontColor($r('app.color.text_secondary'));
              TextInput({ placeholder: '数据分析、新媒体运营', text: this.editAbilities })
                .onChange((v: string) => this.editAbilities = v);
              Text('个人简介').fontSize(AppTheme.CAPTION_SIZE).fontColor($r('app.color.text_secondary'));
              TextInput({ placeholder: '一句话介绍自己', text: this.editSummary })
                .onChange((v: string) => this.editSummary = v);
            };
            Row({ space: 12 }) {
              Button('取消')
                .backgroundColor($r('app.color.divider'))
                .fontColor($r('app.color.text_primary'))
                .layoutWeight(1)
                .onClick(() => {
                  if (this.profile) {
                    this.syncEditsFromProfile(this.profile);
                  }
                  this.isEditing = false;
                  this.message = '';
                });
              Button(this.saving ? '保存中...' : '保存画像')
                .backgroundColor($r('app.color.primary'))
                .layoutWeight(1)
                .enabled(!this.saving)
                .onClick(() => this.saveProfile());
            };
          } else {
            // 查看模式
            Column({ space: 8 }) {
              this.profileField('昵称', this.profile.nickname);
              this.profileField('地区', this.profile.region || '未填写');
              this.profileField('学历', this.profile.education || '未填写');
              this.profileField('专业', this.profile.major || '未填写');
              this.profileField('状态', this.profile.status || '未填写');
              this.profileField('意向', this.profile.intents.length > 0 ? this.profile.intents.join('、') : '未填写');
              this.profileField('能力', this.profile.abilities.length > 0 ? this.profile.abilities.join('、') : '未填写');
              this.profileField('简介', this.profile.summary || '未填写');
            }
            .alignItems(HorizontalAlign.Start)
            .padding(AppTheme.PAGE_PADDING)
            .width('100%')
            .backgroundColor($r('app.color.surface'))
            .borderRadius(AppTheme.CARD_RADIUS);
            Button('编辑画像')
              .width('100%')
              .backgroundColor($r('app.color.primary'))
              .onClick(() => {
                this.isEditing = true;
                this.message = '';
              });
          }
        }

        if (this.message.length > 0 && !this.loading && this.profile !== null) {
          Text(this.message)
            .fontSize(AppTheme.BODY_SIZE)
            .fontColor(this.message.includes('成功') ? $r('app.color.primary') : $r('app.color.danger'))
            .width('100%');
        }
      }
      .padding(AppTheme.PAGE_PADDING);
    }
    .backgroundColor($r('app.color.app_background'));
  }

  @Builder
  profileField(label: string, value: string) {
    Row() {
      Text(label)
        .fontSize(AppTheme.CAPTION_SIZE)
        .fontColor($r('app.color.text_secondary'))
        .width(60);
      Text(value)
        .fontSize(AppTheme.BODY_SIZE)
        .fontColor($r('app.color.text_primary'))
        .layoutWeight(1);
    };
  }
}
