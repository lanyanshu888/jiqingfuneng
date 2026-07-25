import { common } from '@kit.AbilityKit';
import { preferences } from '@kit.ArkData';
import { hilog } from '@kit.PerformanceAnalysisKit';

const DEMO_KEY = 'jiqing_demo_mode';
const STORE_NAME = 'jiqing_demo_state';

export class DemoState {
  private static preferencesStore: preferences.Preferences | null = null;
  private static memoryValue: boolean = false;
  private static readyResolve: (() => void) | null = null;
  private static readyPromise: Promise<void> = new Promise<void>((resolve) => {
    DemoState.readyResolve = resolve;
  });

  static async initialize(context: common.UIAbilityContext): Promise<void> {
    try {
      hilog.info(0x0000, 'JiqingZhiyin', 'DemoState.initialize start');
      DemoState.preferencesStore = await preferences.getPreferences(context, STORE_NAME);
      const raw = await DemoState.preferencesStore.get(DEMO_KEY, false) as boolean;
      DemoState.memoryValue = raw;
      AppStorage.setOrCreate<boolean>(DEMO_KEY, raw);
      hilog.info(0x0000, 'JiqingZhiyin', `DemoState.initialize read value: ${raw}`);
    } catch (error) {
      hilog.warn(0x0000, 'JiqingZhiyin', `DemoState.initialize failed: ${JSON.stringify(error)}`);
      DemoState.preferencesStore = null;
    } finally {
      if (DemoState.readyResolve) {
        DemoState.readyResolve();
        DemoState.readyResolve = null;
      }
    }
  }

  static async waitReady(): Promise<void> {
    await DemoState.readyPromise;
  }

  static enter(): void {
    hilog.info(0x0000, 'JiqingZhiyin', 'DemoState.enter');
    DemoState.memoryValue = true;
    AppStorage.setOrCreate<boolean>(DEMO_KEY, true);
    DemoState.write(true);
  }

  static exit(): void {
    hilog.info(0x0000, 'JiqingZhiyin', 'DemoState.exit');
    DemoState.memoryValue = false;
    AppStorage.setOrCreate<boolean>(DEMO_KEY, false);
    DemoState.write(false);
  }

  static isActive(): boolean {
    return DemoState.memoryValue;
  }

  private static async write(value: boolean): Promise<void> {
    if (DemoState.preferencesStore === null) {
      hilog.warn(0x0000, 'JiqingZhiyin', 'DemoState.write skipped: store is null');
      return;
    }
    try {
      await DemoState.preferencesStore.put(DEMO_KEY, value);
      await DemoState.preferencesStore.flush();
      hilog.info(0x0000, 'JiqingZhiyin', `DemoState.write flushed: ${value}`);
    } catch (error) {
      hilog.warn(0x0000, 'JiqingZhiyin', `DemoState.write failed: ${JSON.stringify(error)}`);
      DemoState.preferencesStore = null;
    }
  }
}
