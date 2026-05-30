import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

export default function SalePayment(props) {
  return <ModelCrudPage {...modelConfigs.SalePayment} {...props} />;
}
