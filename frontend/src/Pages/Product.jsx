import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

export default function Product(props) {
  return <ModelCrudPage {...modelConfigs.Product} {...props} />;
}
