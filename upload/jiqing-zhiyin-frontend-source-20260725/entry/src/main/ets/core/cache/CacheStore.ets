import { common } from '@kit.AbilityKit';
import { preferences } from '@kit.ArkData';

interface CacheEnvelope<T> {
  savedAt: number;
  data: T;
}

export class CacheStore {
  private memoryValues: Map<string, string> = new Map();
  private preferencesStore: preferences.Preferences | null = null;

  async initialize(context: common.UIAbilityContext): Promise<void> {
    try {
      this.preferencesStore = await preferences.getPreferences(context, 'jiqing_growth_cache');
    } catch (error) {
      this.preferencesStore = null;
    }
  }

  makeKey(userId: number, namespace: string): string {
    return `jiqing.cache.user.${userId}.${namespace}`;
  }

  async put<T>(userId: number, namespace: string, value: T): Promise<void> {
    const envelope: CacheEnvelope<T> = {
      savedAt: Date.now(),
      data: value
    };
    const key = this.makeKey(userId, namespace);
    const serialized = JSON.stringify(envelope);
    this.memoryValues.set(key, serialized);
    if (this.preferencesStore !== null) {
      try {
        await this.preferencesStore.put(key, serialized);
        await this.preferencesStore.flush();
      } catch (error) {
        this.preferencesStore = null;
      }
    }
  }

  async get<T>(userId: number, namespace: string): Promise<T | null> {
    const key = this.makeKey(userId, namespace);
    let raw = this.memoryValues.get(key);
    if (!raw && this.preferencesStore !== null) {
      try {
        raw = await this.preferencesStore.get(key, '') as string;
        if (raw.length > 0) {
          this.memoryValues.set(key, raw);
        }
      } catch (error) {
        this.preferencesStore = null;
      }
    }
    if (!raw || raw.length === 0) {
      return null;
    }
    const envelope = JSON.parse(raw) as CacheEnvelope<T>;
    return envelope.data;
  }

  async removeUser(userId: number): Promise<void> {
    const prefix = `jiqing.cache.user.${userId}.`;
    const keys = Array.from(this.memoryValues.keys());
    keys.forEach((key) => {
      if (key.startsWith(prefix)) {
        this.memoryValues.delete(key);
      }
    });
    if (this.preferencesStore !== null) {
      try {
        for (let index = 0; index < keys.length; index++) {
          const key = keys[index];
          if (key.startsWith(prefix)) {
            await this.preferencesStore.delete(key);
          }
        }
        await this.preferencesStore.flush();
      } catch (error) {
        this.preferencesStore = null;
      }
    }
  }
}

export const cacheStore = new CacheStore();
