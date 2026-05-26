import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

export default function PurchasePayment(props) {
  return <ModelCrudPage {...modelConfigs.PurchasePayment} {...props} />;
}
