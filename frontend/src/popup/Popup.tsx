import * as React from 'react';
import {AxiosInstance} from 'axios';
import {browser, Tabs} from 'webextension-polyfill-ts';

import './styles.scss';
import {getConfig} from '../Config';
import {createTask, getHttpClient} from '../Client';

type DownloadResult = string;

const promiseClient = getConfig().then((config) => getHttpClient(config));

function openWebPage(url: string): Promise<Tabs.Tab> {
  return browser.tabs.create({url});
}

async function downloadCurrentTab(
  client: AxiosInstance
): Promise<DownloadResult> {
  const tabs = await browser.tabs.query({
    active: true,
    lastFocusedWindow: true,
  });
  const {url} = tabs[0];
  if (url) {
    const result = await createTask(client)({url});
    return result.statusText;
  } else {
    console.emoji('🦄', 'Current Tab Undefined');
    return 'Current Tab URL undefined';
  }
}

const Popup: React.FC = () => {
  return (
    <section id="popup">
      <h2>Awesome-DL</h2>
      <div id="main__activity">
        <ul>
          <li>
            <button
              type="button"
              onClick={(): Promise<DownloadResult> => {
                return promiseClient.then((client) =>
                  downloadCurrentTab(client)
                );
              }}
            >
              Download
            </button>
          </li>
        </ul>
      </div>
      <div id="links__holder">
        <ul>
          <li>
            <button
              id="options__button"
              type="button"
              onClick={(): Promise<Tabs.Tab> => {
                return openWebPage('options.html#settings');
              }}
            >
              Settings
            </button>
          </li>
          <li>
            <button
              id="options__button"
              type="button"
              onClick={(): Promise<Tabs.Tab> => {
                return openWebPage('options.html#downloads');
              }}
            >
              Downloads
            </button>
          </li>
        </ul>
      </div>
    </section>
  );
};

export default Popup;
