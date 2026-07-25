export type NetworkListener = (online: boolean) => void;

export class NetworkState {
  private online: boolean = true;
  private listeners: NetworkListener[] = [];

  isOnline(): boolean {
    return this.online;
  }

  setOnlineForTest(online: boolean): void {
    this.online = online;
    this.listeners.forEach((listener) => listener(online));
  }

  subscribe(listener: NetworkListener): () => void {
    this.listeners.push(listener);
    listener(this.online);
    return () => {
      this.listeners = this.listeners.filter((item) => item !== listener);
    };
  }
}

export const networkState = new NetworkState();

