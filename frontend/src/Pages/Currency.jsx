import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

export default function Currency(props) {
  return <ModelCrudPage {...modelConfigs.Currency} {...props} />;
}
