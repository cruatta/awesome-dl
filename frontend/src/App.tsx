import React from 'react';
import logo from './logo.svg';
import './App.css';
import { TasksListView, AddTaskView } from './tasks'
import { SettingsView } from "./settings";

function App() {
  return (
    <div className="App">
        <SettingsView />
        <div className="App-header">
          <AddTaskView />
          <TasksListView />
      </div>
    </div>
  );
}

export default App;
