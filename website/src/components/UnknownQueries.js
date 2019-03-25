import React from 'react';
import { fetchData } from '../utils/Util';

/* 
This component lists multiple DocumentItems
*/
export default class UnknownQueries extends React.Component {
  deleteAnswer = async (e, i) => {
    e.preventDefault();
    const data = { data: { query_text: this.props.queries[i].query_text } };
    fetchData(
      process.env.REACT_APP_SERVER_URL + 'v1/web/unknown_query',
      'DELETE',
      data
    ).then(() => {
      this.props.changeView('main');
    });
  };

  render() {
    // Maps through every DocumentItem and display them
    // Each DocumentItem represents a document from the conflict_ids collection
    let queries;

    queries = this.props.queries.map((query, i) => (
      <div
        key={i}
        style={{ float: "left" }}
      >
        <p>
          {query.query_text}
        </p>
        <button
          type="button" className="deleteText" onClick={e => this.deleteAnswer(e, i)}>
          Slett spørsmål
          </button>
      </div>
    ));
    return (
      <div className="itemList">
        <h1>{this.props.title}</h1>
        <div>
          {queries}

        </div>
      </div>
    );
  }
}
