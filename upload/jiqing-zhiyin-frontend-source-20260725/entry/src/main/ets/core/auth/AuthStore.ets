import { asset } from '@kit.AssetStoreKit';
import { UserSummary } from '../../models/AuthModels';
import { TokenProvider } from '../http/ApiClient';

const TOKEN_ALIAS = 'jiqing.zhiyin.auth.token';

export class AuthStore implements TokenProvider {
  private token: string = '';
  private user: UserSummary | null = null;

  async save(token: string, user: UserSummary): Promise<void> {
    this.token = token;
    this.user = user;
    await this.saveTokenToAssetStore(token);
  }

  async getToken(): Promise<string> {
    if (this.token.length > 0) {
      return this.token;
    }
    this.token = await this.loadTokenFromAssetStore();
    return this.token;
  }

  async getUser(): Promise<UserSummary | null> {
    return this.user;
  }

  async clear(): Promise<void> {
    this.token = '';
    this.user = null;
    await this.removeTokenFromAssetStore();
  }

  private async saveTokenToAssetStore(token: string): Promise<void> {
    await this.removeTokenFromAssetStore();
    const attributes: asset.AssetMap = new Map<asset.Tag, asset.Value>();
    attributes.set(asset.Tag.ALIAS, this.toBytes(TOKEN_ALIAS));
    attributes.set(asset.Tag.SECRET, this.toBytes(token));
    attributes.set(asset.Tag.ACCESSIBILITY, asset.Accessibility.DEVICE_FIRST_UNLOCKED);
    attributes.set(asset.Tag.AUTH_TYPE, asset.AuthType.NONE);
    attributes.set(asset.Tag.SYNC_TYPE, asset.SyncType.NEVER);
    try {
      await asset.add(attributes);
    } catch (error) {
      this.token = token;
    }
  }

  private async loadTokenFromAssetStore(): Promise<string> {
    const query: asset.AssetMap = new Map<asset.Tag, asset.Value>();
    query.set(asset.Tag.ALIAS, this.toBytes(TOKEN_ALIAS));
    query.set(asset.Tag.RETURN_TYPE, asset.ReturnType.ALL);
    query.set(asset.Tag.RETURN_LIMIT, 1);
    try {
      const results = await asset.query(query);
      if (results.length === 0) {
        return '';
      }
      const secret = results[0].get(asset.Tag.SECRET) as Uint8Array;
      return this.fromBytes(secret);
    } catch (error) {
      return '';
    }
  }

  private async removeTokenFromAssetStore(): Promise<void> {
    const query: asset.AssetMap = new Map<asset.Tag, asset.Value>();
    query.set(asset.Tag.ALIAS, this.toBytes(TOKEN_ALIAS));
    try {
      await asset.remove(query);
    } catch (error) {
    }
  }

  private toBytes(value: string): Uint8Array {
    const bytes = new Uint8Array(value.length);
    for (let index = 0; index < value.length; index++) {
      bytes[index] = value.charCodeAt(index);
    }
    return bytes;
  }

  private fromBytes(bytes: Uint8Array): string {
    let value = '';
    for (let index = 0; index < bytes.length; index++) {
      value += String.fromCharCode(bytes[index]);
    }
    return value;
  }
}

export const authStore = new AuthStore();
