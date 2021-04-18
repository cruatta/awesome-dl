import * as React from 'react';

import {useState} from 'react';
import {getConfig, setConfig} from '../config';
import 'react-tabs/style/react-tabs.css';
import {Button, TextField} from "@material-ui/core";

export const Settings: React.FC = () => {
  const [baseURL, setBaseURL] = useState(window.location.href);
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
          <TextField
            type="text"
            id="outlined-basic"
            variant="outlined"
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
          <TextField
            type="text"
            id="outlined-basic"
            variant="outlined"
            name="apiKey"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            spellCheck="false"
            autoComplete="off"
            required
          />
        </p>
        <p>
          <Button variant="contained" color="primary" type="submit">
            Save
          </Button>
        </p>
      </form>
    </div>
  );
};