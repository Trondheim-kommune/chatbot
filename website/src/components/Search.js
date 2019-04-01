import React from 'react';
import { fetchData } from '../utils/Util';
import DocumentList from './DocumentList';

/* 
This component is a search bar. You search by url and get a DocumentList
containing the search results
*/
export default class Search extends React.Component {
  state = {
    url: '',
    fetched: false,
  };

  handleSubmit = async e => {
    e.preventDefault();

    // Title and ID based on URL.
    const content = await fetchData(
      process.env.REACT_APP_SERVER_URL + 'v1/web/docs/?url=' + this.state.url,
      'GET',
    );

    if (content.length === 0) {
      alert('Vi fant ingen for den siden, sjekk om URLen stemmer.');
    } else if (content.length > 0) {
      this.setState({ fetched: true, docs: content });
    }
  };

  render() {
    return (
      <div>
        <form onSubmit={e => this.handleSubmit(e)}>
          <label>
            URL:
            <input
              type="text"
              className="searchInputField"
              value={this.state.url}
              name="url"
              placeholder="https://www.trondheim.kommune.no/"
              onChange={e => this.setState({ url: e.target.value })}
            />
          </label>
          <input type="submit" value="Search" className="submitSearch" />
        </form>
        {/* If data i fetched, render a DocumentList with the search results */}
        {this.state.fetched && (
          <DocumentList
            title="Søkeresultater"
            docs={this.state.docs}
            changeView={this.props.changeView}
          />
        )}
      </div>
    );
  }
}
