import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

export default function PurchaseItem(props) {
  return <ModelCrudPage {...modelConfigs.PurchaseItem} {...props} />;
}
