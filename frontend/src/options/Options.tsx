import * as React from 'react';

import {Tab, Tabs, TabList, TabPanel} from 'react-tabs';
import {useState} from 'react';
import {Settings} from './Settings';
import './styles.scss';
import 'react-tabs/style/react-tabs.css';
import {Downloads} from './Downloads';

const Options: React.FC = () => {
  const [tabIndex, setTabIndex] = useState(0);

  return (
    <Tabs
      selectedIndex={tabIndex}
      onSelect={(index): void => setTabIndex(index)}
    >
      <TabList>
        <Tab>
          <a id="downloads">Downloads</a>
        </Tab>
        <Tab>
          <a id="settings">Settings</a>
        </Tab>
      </TabList>
      <TabPanel>
        <div>
          <Downloads />
        </div>
      </TabPanel>
      <TabPanel>
        <div>
          <Settings />
        </div>
      </TabPanel>
    </Tabs>
  );
};

export default Options;
