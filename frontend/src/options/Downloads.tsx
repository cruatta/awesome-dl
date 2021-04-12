import * as React from 'react';

import './styles.scss';
import 'react-tabs/style/react-tabs.css';
import {useState} from 'react';
import {AxiosInstance} from 'axios';
import {ProgressModel, SubmittedTaskModel, TaskStatus} from '../Client/typing';
import {getHttpClient, getTaskProgress, taskListAll} from '../Client';
import {getConfig} from '../Config';

const promiseClient: Promise<AxiosInstance> = getConfig().then((config) =>
  getHttpClient(config)
);

export const Progress: React.FC<{
  progress: ProgressModel;
}> = ({progress}) => {
  return (
    <div className="Progress">
      <progress value={progress.percent_complete} max="100" />
    </div>
  );
};

export const Task: React.FC<{
  task: SubmittedTaskModel;
}> = ({task}) => {
  const statusName = TaskStatus[task.status];
  return (
    <div className="Task">
      <div>Url</div>
      <div>{task.url}</div>
      <div>Status</div>
      <div>{statusName}</div>
      <div>Started</div>
      <div>{task.submitted_ts}</div>
    </div>
  );
};

const TaskWithProgress: React.FC<{
  task: SubmittedTaskModel;
  progress: ProgressModel | undefined;
}> = ({task, progress}) => {
  console.log(progress);
  if (progress) {
    return (
      <li key={task.uuid}>
        <Task task={task} />
        <Progress progress={progress} />
      </li>
    );
  }
  return (
    <li key={task.uuid}>
      <Task task={task} />
    </li>
  );
};

export const TasksList: React.FC = () => {
  const [tasksMap, setTasksMap] = useState(
    new Map<string, SubmittedTaskModel>()
  );
  const [progressMap, setProgressMap] = useState(
    new Map<string, ProgressModel>()
  );

  React.useEffect(() => {
    async function handleLoad(): Promise<void> {
      const client = await promiseClient;
      const list = await taskListAll(client)();
      setTasksMap(
        list.data.reduce((map: Map<string, SubmittedTaskModel>, each) => {
          return map.set(each.uuid, each);
        }, new Map<string, SubmittedTaskModel>())
      );

      const progressModels = [];
      for (const each of list.data) {
        const progressModel = await getTaskProgress(client)(each.uuid);
        if (progressModel.data.length === 1) {
          progressModels.push({
            uuid: each.uuid,
            progress: progressModel.data[0],
          });
        }
      }
      setProgressMap(
        progressModels.reduce((map: Map<string, ProgressModel>, each) => {
          return map.set(each.uuid, each.progress);
        }, new Map<string, ProgressModel>())
      );
    }
    handleLoad();
  }, []);

  console.log('Rendering Tasks...');
  if (progressMap.size === 0 || tasksMap.size === 0) {
    return <div />;
  }
  return (
    <div>
      <ul>
        {Array.from(tasksMap.values()).map((value: SubmittedTaskModel) => {
          return (
            <TaskWithProgress
              key={value.uuid}
              task={value}
              progress={progressMap.get(value.uuid)}
            />
          );
        })}
      </ul>
    </div>
  );
};

export const Downloads: React.FC = () => {
  return <TasksList />;
};
