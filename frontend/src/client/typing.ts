export type DownloadRequestModel = {
  url: string;
  profile?: string;
};

export type SubmittedTaskModel = {
  uuid: string;
  url: string;
  submitted_ts: string;
  status: number;
  profile?: string;
};

// eslint-disable-next-line no-shadow
export enum TaskStatus {
  Created = 0,
  Processing = 1,
  Cancelled = 2,
  Done = 3,
  Failed = 4,
};

export type ProgressModel = {
  status: number;
  percent_complete: string;
  total_size: string;
  speed: string;
  eta: string;
};
