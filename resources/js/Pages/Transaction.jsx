import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

export default function Transaction(props) {
  return <ModelCrudPage {...modelConfigs.Transaction} {...props} />;
}
