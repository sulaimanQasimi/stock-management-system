import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

export default function SaleItem(props) {
  return <ModelCrudPage {...modelConfigs.SaleItem} {...props} />;
}
