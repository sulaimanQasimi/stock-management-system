import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

export default function Expense(props) {
  return <ModelCrudPage {...modelConfigs.Expense} {...props} />;
}
