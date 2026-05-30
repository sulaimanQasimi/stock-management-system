import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

export default function Sale(props) {
  return <ModelCrudPage {...modelConfigs.Sale} {...props} />;
}
