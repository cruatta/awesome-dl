import * as React from 'react';
import {useState} from 'react';

import 'react-tabs/style/react-tabs.css';
import {AxiosInstance} from 'axios';
import {ProgressModel, SubmittedTaskModel, TaskStatus} from '../client/typing';
import {getHttpClient, getTaskProgress, taskListAll} from '../client';
import {getConfig} from '../config';
import {Grid} from "@material-ui/core";

const promiseClient: Promise<AxiosInstance> = (
  getHttpClient(getConfig())
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
  if (progress && task.status !== TaskStatus.Failed) {
    return (
      <div>
        <Task task={task} />
        <Progress progress={progress} />
      </div>
    );
  }
  return (
    <div>
      <Task task={task} />
    </div>
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
      let list: SubmittedTaskModel[] = [];
      try {
          const response = await taskListAll(client)();
          list = response.data
      } catch (e) { }
      setTasksMap(
        list.reduce((map: Map<string, SubmittedTaskModel>, each) => {
          return map.set(each.uuid, each);
        }, new Map<string, SubmittedTaskModel>())
      );

      const progressModels = [];
      for (const each of list) {
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
        <Grid
            container
            direction="column"
            justify="flex-start"
            alignItems="stretch"
        >
            {Array.from(tasksMap.values()).map((value: SubmittedTaskModel) => {
                return (
                    <Grid container item xs={12} spacing={0}>
                    <TaskWithProgress
                        key={value.uuid}
                        task={value}
                        progress={progressMap.get(value.uuid)}
                    />
                    </Grid>
                );
            })}
        </Grid>
    </div>
  );
};
