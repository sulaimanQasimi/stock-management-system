import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

export default function ExpenseType(props) {
  return <ModelCrudPage {...modelConfigs.ExpenseType} {...props} />;
}
