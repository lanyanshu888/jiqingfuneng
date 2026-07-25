import { AbilityConstant, UIAbility, Want } from '@kit.AbilityKit';
import { hilog } from '@kit.PerformanceAnalysisKit';
import { window } from '@kit.ArkUI';
import { cacheStore } from '../core/cache/CacheStore';
import { DemoState } from '../state/DemoState';

export default class EntryAbility extends UIAbility {
  onCreate(want: Want, launchParam: AbilityConstant.LaunchParam): void {
    hilog.info(0x0000, 'JiqingZhiyin', 'EntryAbility created');
    cacheStore.initialize(this.context).catch(() => {
      hilog.warn(0x0000, 'JiqingZhiyin', 'CacheStore falls back to memory mode');
    });
    DemoState.initialize(this.context).catch(() => {
      hilog.warn(0x0000, 'JiqingZhiyin', 'DemoState falls back to memory mode');
    });
  }

  onWindowStageCreate(windowStage: window.WindowStage): void {
    windowStage.loadContent('pages/Index', (err) => {
      if (err.code) {
        hilog.error(0x0000, 'JiqingZhiyin', 'Load content failed: %{public}s', JSON.stringify(err));
      }
    });
  }
}
