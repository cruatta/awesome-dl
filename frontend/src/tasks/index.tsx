import * as React from "react";
import { AddTask } from './add'
import {TasksList} from "./list";

export const AddTaskView: React.FC = () => {
    return <AddTask />;
}
export const TasksListView: React.FC = () => {
    return <TasksList />;
};
