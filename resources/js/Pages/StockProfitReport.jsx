import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

export default function StockProfitReport(props) {
  return <ModelCrudPage {...modelConfigs.StockProfitReport} {...props} />;
}
