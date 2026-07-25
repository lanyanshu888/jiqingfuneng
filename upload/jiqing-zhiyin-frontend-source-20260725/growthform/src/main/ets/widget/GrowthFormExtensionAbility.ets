import { FormExtensionAbility, formBindingData } from '@kit.FormKit';

export default class GrowthFormExtensionAbility extends FormExtensionAbility {
  onAddForm(): formBindingData.FormBindingData {
    return formBindingData.createFormBindingData({
      loggedIn: false,
      taskTitle: '登录冀青智引，查看今日成长任务',
      progress: 0,
      deadlineText: '',
      route: 'login'
    });
  }
}

