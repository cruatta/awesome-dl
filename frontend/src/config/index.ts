const configKey = 'config';

export interface Config {
  baseURL: string;
  apiKey: string;
}

export function setConfig(baseURL: string, apiKey: string): void {
  localStorage.setItem(configKey, JSON.stringify({
      baseURL,
      apiKey,
    })
  );
}

export function getConfig(): Config {
  const configString = localStorage.getItem(configKey);
  if(configString) {
    return JSON.parse(configString) as Config;
  }
  return {
    baseURL: new URL(window.location.href).origin,
    apiKey: 'foobar',
  };
}