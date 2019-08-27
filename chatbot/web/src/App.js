import React, { Component } from 'react';
import Search from './components/Search';
import DocumentList from './components/DocumentList';
import UnknownQueries from './components/UnknownQueries';
import { fetchData } from './utils/Util';
import DocumentView from './components/DocumentView';
import { Layout, Menu } from 'antd';
import css from './App.module.css';

const { Header, Content } = Layout;

class App extends Component {
  state = {
    conflictDocs: [],
    view: 'main',
  };

  fetchAllConflictIDs = async () => {
    const conflictDocs = await fetchData(
      process.env.REACT_APP_SERVER_URL + 'v2/conflict_ids/',
      'GET'
    );
    this.setState({ conflictDocs });
  };

  fetchAllUnknownQueries = async () => {
    const queries = await fetchData(
      process.env.REACT_APP_SERVER_URL + 'v2/unknown_queries/',
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
      <Layout className={css.rootLayout}>
        <Header>
          <Menu
            theme="dark"
            mode="horizontal"
            defaultSelectedKeys={['1']}
            className={css.menu}
          >
            <Menu.Item
              key="1"
              onClick={() => this.setState({ view: 'main' })}
            >
              Home
            </Menu.Item>
          </Menu>
        </Header>

        <Content className={css.contentContainer}>
          <div className={css.content}>
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
        </Content>
      </Layout>
    );
  }
}

export default App;
