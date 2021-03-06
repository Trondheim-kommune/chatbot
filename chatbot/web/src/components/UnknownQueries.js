import React from 'react';
import { fetchData } from '../utils/Util';
import { Typography, Table } from 'antd';

const { Title } = Typography;

export default class UnknownQueries extends React.Component {
  deleteAnswer = async i => {
    const data = this.props.queries[i].query_text;

    await fetchData(
      process.env.REACT_APP_SERVER_URL + 'v2/unknown_queries/' + data + '/',
      'DELETE'
    );

    this.props.changeView('main');
  };

  render() {
    const DeleteButton = (text, record) => (
      <span>
        <a onClick={() => this.deleteAnswer(record.key)}>Slett</a>
      </span>
    );

    const columns = [{
      title: 'Spørring',
      dataIndex: 'query',
      key: 'query',
    }, {
      title: 'Handling',
      key: 'action',
      render: DeleteButton,
    }];

    const data = this.props.queries.map((query, i) => ({
      query: query.query_text,
      key: i,
    }));

    return (
      <div className="itemList">
        <Title level={2}>Ukjente spørringer</Title>

        <Table
          columns={columns}
          dataSource={data}
          pagination={false}
        />
      </div>
    );
  }
}
