import React from 'react';
import { Typography, Table } from 'antd';
import css from './DocumentList.module.css';
import classNames from 'classnames';

const { Title } = Typography;

const DocumentList = ({ docs, changeView, title }) => {
  const ViewButton = (text, record) => (
    <span>
      <a onClick={() => changeView('document', record.id)}>{text}</a>
    </span>
  );

  const columns = [{
    title: 'Title',
    dataIndex: 'title',
    key: 'titlte',
    render: ViewButton,
  }, {
    title: 'ID',
    dataIndex: 'id',
    key: 'id',
  }];

  const data = docs.map(doc => ({
    ...doc,
    key: doc.id,
  }));

  return (
    <div className={classNames(css.itemList, 'itemList')}>
      <Title level={2}>{title}</Title>

      <Table
        columns={columns}
        dataSource={data}
        pagination={false}
      />
    </div>
  );
};

export default DocumentList;