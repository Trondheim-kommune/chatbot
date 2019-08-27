import React from 'react';
import { fetchDataWithoutTypeHeader } from '../utils/Util';
import DocumentList from './DocumentList';
import { Input } from 'antd';
import css from './Search.module.css';
import classNames from 'classnames';

const { Search } = Input;

/* 
This component is a search bar. You search by url and get a DocumentList
containing the search results
*/
export default class SearchBar extends React.Component {
  state = {
    fetched: false,
  };

  handleSearch = async url => {
    // Title and ID based on URL.
    const content = await fetchDataWithoutTypeHeader(
      process.env.REACT_APP_SERVER_URL + 'v2/contents/?url=' + url.toString(),
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
        <Search
          className={classNames(css.search, 'searchInputField')}
          placeholder="Search for an URL"
          onSearch={this.handleSearch}
          enterButton
        />

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
