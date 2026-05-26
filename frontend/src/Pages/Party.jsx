import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

export default function Party(props) {
  return <ModelCrudPage {...modelConfigs.Party} {...props} />;
}
