import React from 'react';
import ModelCrudPage from './Shared/ModelCrudPage';
import { modelConfigs } from './modelConfigs';

type RecordItem = {
  id: number;
  [key: string]: string | number | null | undefined;
};

type ModelPageProps = {
  [key: string]: unknown;
  options?: Record<string, Array<{ value: number | string; label: string }>>;
};

export function createModelPage(configKey: keyof typeof modelConfigs, propName: string) {
  return function ModelPage(props: ModelPageProps) {
    const records = (props[propName] || []) as RecordItem[];

    return (
      <ModelCrudPage
        {...modelConfigs[configKey]}
        records={records}
        options={props.options || {}}
      />
    );
  };
}
