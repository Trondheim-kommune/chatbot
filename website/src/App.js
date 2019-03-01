import React, { Component } from 'react';
import Search from './components/Search';
import DocumentList from './components/DocumentList';
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
      process.env.REACT_APP_SERVER_URL + 'v1/get_all_conflict_ids',
      {},
    );
    this.setState({ conflictDocs });
  };

  async componentDidMount() {
    this.fetchAllConflictIDs();
  }

  changeView = async (view, id) => {
    this.setState({ view, id });
    this.fetchAllConflictIDs();
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
