import {browser} from 'webextension-polyfill-ts';

const configKey = 'config';

export interface Config {
  baseURL: string;
  apiKey: string;
}

export async function setConfig(baseURL: string, apiKey: string): Promise<void> {
  await browser.storage.local.set({
    configKey: {
      baseURL,
      apiKey,
    },
  });
}

export async function getConfig(): Promise<Config> {
  const keys = await browser.storage.local.get(configKey);
  if (keys.config) {
    return keys.config;
  } else {
    return {
      baseURL: 'http://localhost:8080',
      apiKey: 'foobar',
    };
  }
}