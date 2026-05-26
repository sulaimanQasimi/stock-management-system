import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

export default function PurchaseBatch(props) {
  return <ModelCrudPage {...modelConfigs.PurchaseBatch} {...props} />;
}
