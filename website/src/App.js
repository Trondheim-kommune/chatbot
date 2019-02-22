import React, { Component } from 'react';
import './App.css';
import Search from "./components/Search";
import DocumentView from "./components/DocumentView"

class App extends Component {
  render() {
    return (
      <div>
        <Search />
        <DocumentView docs={[{ "title": "lol", "id": "id102" }, { "title": "test2", "id": "34hj234" }]} />
      </div>

    );
  }
}

export default App;
