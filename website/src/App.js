import React, { Component } from 'react';
import Search from './components/Search';
import DocumentList from './components/DocumentList';
import UnknownQueries from './components/UnknownQueries';
import { fetchData } from './utils/Util';
import DocumentView from './components/DocumentView';

class App extends Component {
  state = {
    conflictDocs: [],
    searchDocs: [],
    view: 'main',
    id: '',
  };

  fetchAllConflictIDs = async () => {
    const conflictDocs = await fetchData(
      process.env.REACT_APP_SERVER_URL + 'v1/web/conflict_ids',
      'GET'
    );
    this.setState({ conflictDocs });
  };

  fetchAllUnknownQueries = async () => {
    const queries = await fetchData(
      process.env.REACT_APP_SERVER_URL + 'v1/web/unknown_queries',
      'GET'
    );
    this.setState({ queries });
  };

  async componentDidMount() {
    this.fetchAllConflictIDs();
    this.fetchAllUnknownQueries();
  }

  changeView = async (view, id) => {
    this.setState({ view, id });
    this.fetchAllConflictIDs();
    this.fetchAllUnknownQueries();
  };

  render() {
    return (
      <div>
        {this.state.view === 'main' && (
          <div>
            <Search changeView={this.changeView} />
            <DocumentList
              title="Konflikter"
              docs={this.state.conflictDocs}
              changeView={this.changeView}
            />
            {this.state.queries &&
              <UnknownQueries
                title="Chatbot fant ikke svar på disse:"
                queries={this.state.queries}
                changeView={this.changeView}
              />
            }
          </div>
        )}
        {this.state.view === 'document' && (
          <DocumentView id={this.state.id} changeView={this.changeView} />
        )}
      </div>
    );
  }
}

export default App;
