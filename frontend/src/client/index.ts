import Axios, {AxiosInstance, AxiosResponse} from 'axios';
import {Config} from '../config';
import {
  DownloadRequestModel,
  ProgressModel, ResultModel,
  SubmittedTaskModel,
} from './typing';

export async function getHttpClient(config: Config): Promise<AxiosInstance> {
  return Axios.create({
    baseURL: config.baseURL,
    timeout: 1000,
    headers: {'X-ADL-Key': config.apiKey},
  });
}

export function cleanupTasks(
    client: AxiosInstance
): () => Promise<AxiosResponse<ResultModel>> {
  return (): Promise<AxiosResponse<ResultModel>> => {
    return client.post<ResultModel>('/task/cleanup');
  };
}


export function createTask(
  client: AxiosInstance
): (model: DownloadRequestModel) => Promise<AxiosResponse<SubmittedTaskModel>> {
  return (
    model: DownloadRequestModel
  ): Promise<AxiosResponse<SubmittedTaskModel>> => {
    const data = model.profile
      ? {url: model.url, profile: model.profile}
      : {url: model.url};
    return client.post<SubmittedTaskModel>('/ytdl/task', data);
  };
}

export function taskListAll(
  client: AxiosInstance
): () => Promise<AxiosResponse<SubmittedTaskModel[]>> {
  return (): Promise<AxiosResponse<SubmittedTaskModel[]>> => {
    return client.get('/task/all');
  };
}

export function getTaskProgress(
  client: AxiosInstance
): (uuid: string) => Promise<AxiosResponse<Array<ProgressModel>>> {
  return (uuid): Promise<AxiosResponse<Array<ProgressModel>>> => {
    return client.get(`/task/progress/${uuid}`);
  };
}
