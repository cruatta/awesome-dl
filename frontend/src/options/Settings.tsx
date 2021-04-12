import * as React from 'react';

import './styles.scss';
import {useState} from 'react';
import {getConfig, setConfig} from '../Config';
import 'react-tabs/style/react-tabs.css';

export const Settings: React.FC = () => {
  const [baseURL, setBaseURL] = useState('');
  const [apiKey, setApiKey] = useState('');

  React.useEffect(() => {
    async function handleLoad(): Promise<void> {
      const config = await getConfig();
      setApiKey(config.apiKey);
      setBaseURL(config.baseURL);
    }
    handleLoad();
  }, []);

  async function handleSubmit(
    evt: React.FormEvent<HTMLFormElement>
  ): Promise<void> {
    evt.preventDefault();
    await setConfig(baseURL, apiKey);
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <p>
          <label htmlFor="baseURL">Server URL</label>
          <br />
          <input
            type="text"
            id="baseURL"
            name="baseURL"
            value={baseURL}
            onChange={e => setBaseURL(e.target.value)}
            spellCheck="false"
            autoComplete="off"
            required
          />
        </p>
        <p>
          <label htmlFor="apiKey">API Key</label>
          <br />
          <input
            type="text"
            id="apiKey"
            name="apiKey"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            spellCheck="false"
            autoComplete="off"
            required
          />
        </p>
        <p>
          <input type="submit" value="Save" />
        </p>
      </form>
    </div>
  );
};