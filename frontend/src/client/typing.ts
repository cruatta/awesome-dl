export type DownloadRequestModel = {
  url: string;
  profile?: string;
};

export type SubmittedTaskModel = {
  uuid: string;
  url: string;
  submitted_ts: string;
  status: TaskStatus;
  profile?: string;
};

export type ResultModel = {
  ok: boolean;
  output: string;
}

export enum TaskStatus {
  Created = 0,
  Processing = 1,
  Cancelled = 2,
  Done = 3,
  Failed = 4,
}

export type ProgressModel = {
  status: number;
  percent_complete: string;
  total_size: string;
  speed: string;
  eta: string;
};
